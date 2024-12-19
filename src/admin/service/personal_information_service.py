from sqlalchemy.orm import Session

from src.admin.model.outsoring_personal_information_status import (
    OutSourcingPersonalInformationStatus,
)
from src.admin.model.response.PersonalInformationAgreeStatus import (
    PersonalInformationAgreeStatus,
)
from src.admin.routes.port.base_personal_information_service import (
    BasePersonalInformationService,
)
from src.admin.service.port.base_personal_information_repository import (
    BasePersonalInformationRepository,
)
from src.main.transactional import transactional
from src.user.domain.user import User


class PersonalInformationService(BasePersonalInformationService):

    def __init__(self, personal_information_repository: BasePersonalInformationRepository):
        self.personal_information_repository = personal_information_repository

    @transactional
    def update_status(self, to_status: str, user: User, db: Session):
        self.personal_information_repository.update_status(to_status, user, db)

    def get_status(self, db) -> PersonalInformationAgreeStatus:
        status = self.personal_information_repository.get_status(db)
        return PersonalInformationAgreeStatus(status=OutSourcingPersonalInformationStatus(status))
