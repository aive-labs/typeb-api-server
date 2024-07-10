from abc import ABC, abstractmethod

from sqlalchemy.orm import Session

from src.campaign.routes.dto.request.campaign_create import CampaignCreate
from src.core.transactional import transactional
from src.users.domain.user import User


class CreateCampaignUseCase(ABC):

    @transactional
    @abstractmethod
    def create_campaign(self, campaign_create: CampaignCreate, user: User, db: Session):
        pass
