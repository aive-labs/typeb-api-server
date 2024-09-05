from abc import ABC, abstractmethod

from sqlalchemy.orm import Session

from src.core.transactional import transactional
from src.users.domain.user import User


class DeleteCampaignUseCase(ABC):

    @transactional
    @abstractmethod
    def exec(self, campaign_id: str, user: User, db: Session):
        pass
