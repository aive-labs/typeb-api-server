from abc import ABC, abstractmethod

from sqlalchemy.orm import Session

from src.user.domain.user import User


class BasePersonalInformationRepository(ABC):
    @abstractmethod
    def update_status(self, to_status: str, user: User, db: Session):
        pass

    @abstractmethod
    def get_status(self, db: Session) -> str:
        pass
