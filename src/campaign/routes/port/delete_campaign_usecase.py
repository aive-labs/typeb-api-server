from abc import ABC, abstractmethod

from sqlalchemy.orm import Session

from src.main.transactional import transactional
from src.user.domain.user import User


class DeleteCampaignUseCase(ABC):

    @transactional
    @abstractmethod
    def exec(self, campaign_id: str, user: User, db: Session):
        pass
