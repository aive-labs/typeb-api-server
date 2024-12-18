from abc import ABC, abstractmethod

from sqlalchemy.orm import Session

from src.payment.routes.dto.response.cafe24_payment_response import (
    Cafe24PaymentResponse,
)
from src.users.domain.user import User


class GetCafe24PaymentUseCase(ABC):

    @abstractmethod
    async def exec(self, order_id: str, user: User, db: Session) -> Cafe24PaymentResponse:
        pass
