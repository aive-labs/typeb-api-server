from abc import ABC, abstractmethod

from sqlalchemy.orm import Session

from src.campaign.routes.dto.request.campaign_create import CampaignCreate
from src.main.transactional import transactional
from src.user.domain.user import User


class UpdateCampaignUseCase(ABC):

    @transactional
    @abstractmethod
    def exec(
        self, campaign_id: str, campaign_update: CampaignCreate, user: User, db: Session
    ) -> dict:
        pass
