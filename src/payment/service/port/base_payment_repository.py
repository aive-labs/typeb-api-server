from abc import ABC, abstractmethod

from sqlalchemy.orm import Session

from src.payment.domain.payment import Payment
from src.payment.routes.dto.request.pre_data_for_validation import PreDataForValidation
from src.users.domain.user import User


class BasePaymentRepository(ABC):

    @abstractmethod
    def save_pre_data_for_validation(
        self, pre_data_for_validation: PreDataForValidation, user: User, db: Session
    ):
        pass

    @abstractmethod
    def check_pre_validation_data_for_payment(
        self, order_id: str, amount: int, db: Session
    ) -> bool:
        pass

    @abstractmethod
    def delete_pre_validation_data(self, order_id: str, db: Session):
        pass

    @abstractmethod
    def save_history(self, payment: Payment, user: User, db: Session):
        pass
