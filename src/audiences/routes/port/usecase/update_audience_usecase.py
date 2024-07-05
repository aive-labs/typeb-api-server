from abc import ABC, abstractmethod

from sqlalchemy.orm import Session

from src.audiences.routes.dto.request.audience_update import AudienceUpdate
from src.core.transactional import transactional
from src.users.domain.user import User


class UpdateAudienceUseCase(ABC):

    @transactional
    @abstractmethod
    def exec(
        self, audience_id: str, audience_update: AudienceUpdate, user: User, db: Session
    ) -> str:
        pass
