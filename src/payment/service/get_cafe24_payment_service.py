from sqlalchemy.orm import Session

from src.auth.routes.port.base_oauth_service import BaseOauthService
from src.core.exceptions.exceptions import NotFoundException
from src.payment.infra.payment_repository import PaymentRepository
from src.payment.routes.dto.response.cafe24_payment_response import (
    Cafe24PaymentResponse,
)
from src.payment.routes.use_case.get_cafe24_payment_usecase import (
    GetCafe24PaymentUseCase,
)
from src.users.domain.user import User


class GetCafe24PaymentService(GetCafe24PaymentUseCase):

    def __init__(self, cafe24_service: BaseOauthService, payment_repository: PaymentRepository):
        self.cafe24_service = cafe24_service
        self.payment_repository = payment_repository

    async def exec(self, order_id: str, user: User, db: Session) -> Cafe24PaymentResponse:
        self.check_existing_order(order_id, db)

        payment_result = await self.cafe24_service.get_payment(order_id)

        self.payment_repository.save_cafe24_payment(payment_result, user, db)

        return Cafe24PaymentResponse.from_model(payment_result)

    def check_existing_order(self, order_id, db):
        is_existing_order = self.payment_repository.existing_order_by_cafe24_order_id(order_id, db)
        if not is_existing_order:
            raise NotFoundException(detail={"message": "주문 및 결제 정보를 찾지 못했습니다."})