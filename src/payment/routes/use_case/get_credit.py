from abc import ABC, abstractmethod

from sqlalchemy.orm import Session

from src.users.domain.user import User


class GetCreditUseCase(ABC):

    @abstractmethod
    def get_credit(self, user: User, db: Session) -> int:
        pass
