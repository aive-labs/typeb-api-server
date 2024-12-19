from abc import ABC, abstractmethod

from sqlalchemy.orm import Session

from src.audience.routes.dto.request.audience_update import AudienceUpdate
from src.main.transactional import transactional
from src.user.domain.user import User


class UpdateAudienceUseCase(ABC):

    @transactional
    @abstractmethod
    def exec(
        self, audience_id: str, audience_update: AudienceUpdate, user: User, db: Session
    ) -> str:
        pass
