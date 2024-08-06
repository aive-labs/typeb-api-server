from sqlalchemy.orm import Session

from src.admin.infra.entity.personal_variable_entity import PersonalVariablesEntity
from src.admin.routes.dto.response.personal_variable_response import (
    PersonalVariableResponse,
)
from src.admin.service.port.base_admin_repository import BaseAdminRepository
from src.common.enums.access_level import AccessLevel
from src.users.domain.user import User


class AdminRepository(BaseAdminRepository):

    def get_personal_variables(self, user: User, db: Session) -> list[PersonalVariableResponse]:
        access_level = [level.value for level in AccessLevel if level.name == user.role_id][0]

        entities = (
            db.query(PersonalVariablesEntity)
            .filter(PersonalVariablesEntity.access_level >= access_level)
            .all()
        )

        return [PersonalVariableResponse.from_entity(entity) for entity in entities]
