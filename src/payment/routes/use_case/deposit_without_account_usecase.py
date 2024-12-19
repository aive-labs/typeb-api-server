from abc import ABC, abstractmethod

from sqlalchemy.orm import Session

from src.main.transactional import transactional
from src.payment.routes.dto.request.deposit_without_account import DepositWithoutAccount
from src.user.domain.user import User


class DepositWithoutAccountUseCase(ABC):

    @transactional
    @abstractmethod
    def exec(self, deposit_request: DepositWithoutAccount, user: User, db: Session):
        pass

    @transactional
    @abstractmethod
    def complete(self, pending_deposit_id, user, db):
        pass
