from abc import ABC, abstractmethod

from sqlalchemy.orm import Session

from src.content.domain.creatives import Creatives
from src.content.routes.dto.request.creatives_create import CreativeCreate
from src.main.transactional import transactional
from src.user.domain.user import User


class UpdateCreativesUseCase(ABC):

    @transactional
    @abstractmethod
    def update_creative(
        self, creative_id: int, creative_update: CreativeCreate, user: User, db: Session
    ) -> Creatives:
        pass
