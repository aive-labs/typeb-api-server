from abc import ABC, abstractmethod

from sqlalchemy.orm import Session

from src.admin.routes.dto.response.personal_variable_response import (
    PersonalVariableResponse,
)
from src.users.domain.user import User


class GetPersonalVariablesUseCase(ABC):

    @abstractmethod
    def get_personal_variable(self, user: User, db: Session) -> list[PersonalVariableResponse]:
        pass
