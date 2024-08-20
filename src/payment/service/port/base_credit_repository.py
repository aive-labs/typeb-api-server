from abc import ABC, abstractmethod

from sqlalchemy.orm import Session

from src.payment.domain.credit_history import CreditHistory


class BaseCreditRepository(ABC):

    @abstractmethod
    def get_remain_credit(self, db: Session) -> int:
        pass

    @abstractmethod
    def update_credit(self, update_amount, db: Session):
        pass

    @abstractmethod
    def add_history(self, credit_history: CreditHistory, db: Session):
        pass

    @abstractmethod
    def get_history_with_pagination(self, db, current_page, per_page) -> list[CreditHistory]:
        pass

    @abstractmethod
    def get_all_history_count(self, db: Session) -> int:
        pass
