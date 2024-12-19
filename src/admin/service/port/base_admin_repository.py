from abc import ABC, abstractmethod

from sqlalchemy.orm import Session

from src.admin.routes.dto.response.personal_variable_response import (
    PersonalVariableResponse,
)
from src.user.domain.user import User


class BaseAdminRepository(ABC):

    @abstractmethod
    def get_personal_variables(self, user: User, db: Session) -> list[PersonalVariableResponse]:
        pass
