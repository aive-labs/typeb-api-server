from sqlalchemy.orm import Session

from src.admin.routes.dto.response.personal_variable_response import (
    PersonalVariableResponse,
)
from src.admin.routes.port.get_personal_variables_usecase import (
    GetPersonalVariablesUseCase,
)
from src.admin.service.port.base_admin_repository import BaseAdminRepository
from src.user.domain.user import User


class GetPersonalVariablesService(GetPersonalVariablesUseCase):

    def __init__(self, admin_repository: BaseAdminRepository):
        self.admin_repository = admin_repository

    def get_personal_variable(self, user: User, db: Session) -> list[PersonalVariableResponse]:
        return self.admin_repository.get_personal_variables(user, db)
