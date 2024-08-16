from abc import ABC, abstractmethod

from sqlalchemy.orm import Session

from src.payment.routes.dto.request.payment_request import (
    PaymentAuthorizationRequestData,
)
from src.users.domain.user import User


class PaymentUseCase(ABC):

    @abstractmethod
    async def exec(
        self,
        user: User,
        db: Session,
        payment_request: PaymentAuthorizationRequestData | None = None,
    ):
        pass
