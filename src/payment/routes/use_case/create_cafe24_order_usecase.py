from abc import ABC, abstractmethod

from sqlalchemy.orm import Session

from src.payment.routes.dto.request.cafe24_order_request import Cafe24OrderRequest
from src.payment.routes.dto.response.cafe24_order_response import Cafe24OrderResponse
from src.users.domain.user import User


class CreateCafe24OrderUseCase(ABC):

    @abstractmethod
    async def exec(
        self, user: User, db: Session, order_request: Cafe24OrderRequest
    ) -> Cafe24OrderResponse:
        pass
