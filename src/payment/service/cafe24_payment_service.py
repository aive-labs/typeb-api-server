from sqlalchemy.orm import Session

from src.auth.routes.port.base_oauth_service import BaseOauthService
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
        pass
