from abc import ABC, abstractmethod

from src.audiences.routes.dto.request.audience_update import AudienceUpdate
from src.users.domain.user import User


class UpdateAudienceUseCase(ABC):

    @abstractmethod
    def exec(self, audience_id: str, audience_update: AudienceUpdate, user: User):
        pass
