from abc import ABC, abstractmethod

from sqlalchemy.orm import Session

from src.contents.domain.creatives import Creatives
from src.contents.routes.dto.request.creatives_create import CreativeCreate
from src.core.transactional import transactional
from src.users.domain.user import User


class UpdateCreativesUseCase(ABC):

    @transactional
    @abstractmethod
    def update_creative(
        self, creative_id: int, creative_update: CreativeCreate, user: User, db: Session
    ) -> Creatives:
        pass
