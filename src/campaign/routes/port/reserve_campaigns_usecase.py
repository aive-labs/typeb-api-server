from abc import ABC, abstractmethod

from sqlalchemy.orm import Session

from src.core.transactional import transactional
from src.user.domain.user import User


class ReserveCampaignsUseCase(ABC):

    @transactional
    @abstractmethod
    async def reserve_campaigns(self, campaign_id, execution_date, user: User, db: Session) -> dict:
        pass
