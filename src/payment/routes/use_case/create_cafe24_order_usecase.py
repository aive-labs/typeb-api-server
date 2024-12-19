from abc import ABC, abstractmethod

from sqlalchemy.orm import Session

from src.payment.model.request.cafe24_order_request import Cafe24OrderRequest
from src.payment.model.response.cafe24_order_response import Cafe24OrderResponse
from src.user.domain.user import User


class CreateCafe24OrderUseCase(ABC):

    @abstractmethod
    async def exec(
        self, user: User, db: Session, order_request: Cafe24OrderRequest
    ) -> Cafe24OrderResponse:
        pass
