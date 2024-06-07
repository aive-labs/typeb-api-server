from abc import ABC, abstractmethod

from src.campaign.routes.dto.request.campaign_create import CampaignCreate
from src.users.domain.user import User


class CreateCampaignUsecase(ABC):
    @abstractmethod
    def create_campaign(self, campaign_create: CampaignCreate, user: User):
        pass
