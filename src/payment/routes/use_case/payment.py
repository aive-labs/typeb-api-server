from abc import ABC, abstractmethod

from sqlalchemy.orm import Session

from src.payment.routes.dto.request.payment_request import (
    PaymentAuthorizationRequestData,
)
from src.users.domain.user import User


class PaymentUseCase(ABC):

    @abstractmethod
    async def exec(self, payment_request: PaymentAuthorizationRequestData, user: User, db: Session):
        pass
