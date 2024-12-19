from abc import ABC, abstractmethod

from sqlalchemy.orm import Session

from src.campaign.enums.campaign_progress import CampaignProgress
from src.main.transactional import transactional


class UpdateCampaignProgressUseCase(ABC):

    @transactional
    @abstractmethod
    def exec(self, campaign_id: str, update_status: CampaignProgress, db: Session):
        pass
