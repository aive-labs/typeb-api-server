from abc import ABC, abstractmethod

from sqlalchemy.orm import Session

from src.users.domain.user import User


class InvoiceDownloadUseCase(ABC):

    @abstractmethod
    def exec(self, credit_history_id, user: User, db: Session) -> bytes:
        pass
