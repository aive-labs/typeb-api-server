from abc import ABC, abstractmethod

from sqlalchemy.orm import Session


class GetCreditUseCase(ABC):

    @abstractmethod
    def get_credit(self, db: Session) -> int:
        pass
