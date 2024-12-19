from abc import ABC, abstractmethod

from sqlalchemy.orm import Session

from src.payment.model.request.pre_data_for_validation import PreDataForValidation
from src.user.domain.user import User


class SavePreDataForValidation(ABC):

    @abstractmethod
    def save_pre_data_for_validation(
        self, pre_data_for_validation: PreDataForValidation, user: User, db: Session
    ):
        pass
