from sqlalchemy.orm import Session

from src.admin.routes.port.base_personal_information_service import (
    BasePersonalInformationService,
)
from src.admin.service.port.base_personal_information_repository import (
    BasePersonalInformationRepository,
)
from src.core.transactional import transactional
from src.users.domain.user import User


class PersonalInformationService(BasePersonalInformationService):

    def __init__(self, personal_information_repository: BasePersonalInformationRepository):
        self.personal_information_repository = personal_information_repository

    @transactional
    def update_status(self, to_status: str, user: User, db: Session):
        self.personal_information_repository.update_status(to_status, user, db)
