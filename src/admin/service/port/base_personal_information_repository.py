from abc import ABC, abstractmethod

from sqlalchemy.orm import Session

from src.users.domain.user import User


class BasePersonalInformationRepository(ABC):
    @abstractmethod
    def update_status(self, to_status: str, user: User, db: Session):
        pass
