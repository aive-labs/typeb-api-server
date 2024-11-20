from sqlalchemy.orm import Session

from src.auth.routes.port.base_oauth_service import BaseOauthService
from src.core.exceptions.exceptions import ConsistencyException
from src.payment.routes.dto.request.cafe24_order_request import Cafe24OrderRequest
from src.payment.routes.dto.response.cafe24_order_response import Cafe24OrderResponse
from src.payment.routes.use_case.create_cafe24_order_usecase import (
    CreateCafe24OrderUseCase,
)
from src.users.domain.user import User


class Cafe24PaymentService(CreateCafe24OrderUseCase):

    def __init__(self, cafe24_service: BaseOauthService):
        self.cafe24_service = cafe24_service

    async def exec(
        self, user: User, db: Session, order_request: Cafe24OrderRequest
    ) -> Cafe24OrderResponse:
        if user.mall_id is None:
            raise ConsistencyException(detail={"message": "등록된 쇼핑몰 정보가 없습니다."})

        cafe24_order = await self.cafe24_service.create_order(user.mall_id, order_request)

        # cafe24 정보 저장
        #

        return Cafe24OrderResponse.from_model(cafe24_order)
