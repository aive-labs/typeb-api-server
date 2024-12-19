from abc import ABC, abstractmethod

from sqlalchemy.orm import Session

from src.payment.routes.dto.request.payment_request import (
    PaymentRequest,
)
from src.user.domain.user import User


class PaymentUseCase(ABC):

    @abstractmethod
    async def exec(
        self,
        user: User,
        db: Session,
        payment_request: PaymentRequest | None = None,
    ):
        pass
