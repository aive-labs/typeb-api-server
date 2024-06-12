from abc import ABC, abstractmethod

from src.contents.domain.creatives import Creatives
from src.contents.routes.dto.request.creatives_create import CreativeCreate
from src.users.domain.user import User


class UpdateCreativesUseCase(ABC):

    @abstractmethod
    def update_creative(
        self, creative_id: int, creative_update: CreativeCreate, user: User
    ) -> Creatives:
        pass
