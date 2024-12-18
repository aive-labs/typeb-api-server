from abc import ABC, abstractmethod

from sqlalchemy.orm import Session

from src.admin.routes.dto.response.PersonalInformationAgreeStatus import (
    PersonalInformationAgreeStatus,
)
from src.core.transactional import transactional
from src.users.domain.user import User


class BasePersonalInformationService(ABC):

    @transactional
    @abstractmethod
    def update_status(self, to_status: str, user: User, db: Session):
        pass

    @abstractmethod
    def get_status(self, db) -> PersonalInformationAgreeStatus:
        pass
