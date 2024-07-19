from abc import ABC, abstractmethod

from sqlalchemy.orm import Session

from src.campaign.domain.campaign import Campaign
from src.campaign.routes.dto.response.campaign_basic_response import (
    CampaignBasicResponse,
)
from src.campaign.routes.dto.response.campaign_timeline_response import (
    CampaignTimelineResponse,
)
from src.campaign.routes.dto.response.exclusion_customer_detail import (
    ExcludeCustomerDetail,
)
from src.users.domain.user import User


class GetCampaignUseCase(ABC):
    @abstractmethod
    def get_campaigns(self, start_date: str, end_date: str, user: User) -> list[Campaign]:
        pass

    @abstractmethod
    def get_timeline(self, campaign_id: str, db: Session) -> list[CampaignTimelineResponse]:
        pass

    @abstractmethod
    def get_campaign_detail(self, campaign_id, user, db: Session) -> CampaignBasicResponse:
        pass

    @abstractmethod
    def get_exclude_customer(self, campaign_id, user: User, db: Session) -> ExcludeCustomerDetail:
        pass
