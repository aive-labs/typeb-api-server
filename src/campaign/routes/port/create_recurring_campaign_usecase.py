from abc import ABC, abstractmethod

from sqlalchemy.orm import Session

from src.core.transactional import transactional
from src.user.domain.user import User


class CreateRecurringCampaignUseCase(ABC):

    @transactional
    @abstractmethod
    def exec(self, campaign_id, user: User, db: Session) -> dict:
        pass
