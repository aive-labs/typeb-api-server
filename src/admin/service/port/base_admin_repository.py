from abc import ABC, abstractmethod

from src.admin.routes.dto.response.personal_variable_response import (
    PersonalVariableResponse,
)
from src.users.domain.user import User


class BaseAdminRepository(ABC):

    @abstractmethod
    def get_personal_variables(self, user: User) -> list[PersonalVariableResponse]:
        pass
