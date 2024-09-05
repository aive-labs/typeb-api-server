from abc import ABC, abstractmethod

from sqlalchemy.orm import Session

from src.payment.routes.dto.request.payment_request import (
    PaymentRequest,
)
from src.users.domain.user import User


class IssueBillingKeyUseCase(ABC):

    @abstractmethod
    async def issue_billing_key(self, payment_data: PaymentRequest, user: User, db: Session):
        pass
