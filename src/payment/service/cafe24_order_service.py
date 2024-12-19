from sqlalchemy.orm import Session

from src.auth.routes.port.base_oauth_service import BaseOauthService
from src.main.exceptions.exceptions import ConsistencyException
from src.payment.infra.payment_repository import PaymentRepository
from src.payment.model.request.cafe24_order_request import Cafe24OrderRequest
from src.payment.model.response.cafe24_order_response import Cafe24OrderResponse
from src.payment.routes.use_case.create_cafe24_order_usecase import (
    CreateCafe24OrderUseCase,
)
from src.user.domain.user import User


class Cafe24OrderService(CreateCafe24OrderUseCase):

    def __init__(self, cafe24_service: BaseOauthService, payment_repository: PaymentRepository):
        self.cafe24_service = cafe24_service
        self.payment_repository = payment_repository

    async def exec(
        self, user: User, db: Session, order_request: Cafe24OrderRequest
    ) -> Cafe24OrderResponse:
        if user.mall_id is None:
            raise ConsistencyException(detail={"message": "등록된 쇼핑몰 정보가 없습니다."})

        cafe24_order = await self.cafe24_service.create_order(user, order_request)

        # cafe24 주문 정보 DB 저장
        self.payment_repository.save_cafe24_order(cafe24_order, user, db)

        return Cafe24OrderResponse.from_model(cafe24_order)
