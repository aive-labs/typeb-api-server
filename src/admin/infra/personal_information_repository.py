from datetime import datetime, timezone

from sqlalchemy.orm import Session

from src.admin.infra.entity.outsouring_personal_infomation_status_entity import (
    OutSouringPersonalInformationStatusEntity,
)
from src.admin.service.port.base_personal_information_repository import (
    BasePersonalInformationRepository,
)
from src.core.exceptions.exceptions import ConsistencyException
from src.users.domain.user import User


class PersonalInformationRepository(BasePersonalInformationRepository):

    def get_status(self, db) -> str:
        entity = db.query(OutSouringPersonalInformationStatusEntity).first()

        if entity is None:
            raise ConsistencyException("등록된 상태가 없습니다.")

        return entity.term_status

    def update_status(self, to_status: str, user: User, db: Session):
        db.query(OutSouringPersonalInformationStatusEntity).update(
            {
                OutSouringPersonalInformationStatusEntity.term_status: to_status,
                OutSouringPersonalInformationStatusEntity.updated_by: user.user_id,
                OutSouringPersonalInformationStatusEntity.updated_at: datetime.now(timezone.utc),
            }
        )
