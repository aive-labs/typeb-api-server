from abc import ABC, abstractmethod

from sqlalchemy.orm import Session

from src.campaign.routes.dto.request.campaign_set_update import CampaignSetUpdate
from src.core.transactional import transactional
from src.users.domain.user import User


class UpdateCampaignSetUseCase(ABC):

    @transactional
    @abstractmethod
    def update_campaign_set(
        self, campaign_id: str, campaign_set_update: CampaignSetUpdate, user: User, db: Session
    ) -> bool:
        pass
