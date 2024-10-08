from abc import ABC, abstractmethod

from sqlalchemy.orm import Session

from src.payment.domain.pending_deposit import PendingDeposit


class BaseDepositRepository(ABC):

    @abstractmethod
    def save_pending_depository(self, pending_deposit: PendingDeposit, db: Session):
        pass

    @abstractmethod
    def complete(self, pending_deposit_id, user, db) -> PendingDeposit:
        pass

    @abstractmethod
    def get_deposit_by_credit_history_id(self, credit_history_id, db: Session) -> PendingDeposit:
        pass
