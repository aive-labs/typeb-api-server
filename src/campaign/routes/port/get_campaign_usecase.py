from abc import ABC, abstractmethod

from sqlalchemy.orm import Session

from src.campaign.domain.campaign import Campaign
from src.campaign.routes.dto.response.campaign_timeline_response import (
    CampaignTimelineResponse,
)
from src.users.domain.user import User


class GetCampaignUseCase(ABC):
    @abstractmethod
    def get_campaigns(
        self, start_date: str, end_date: str, user: User
    ) -> list[Campaign]:
        pass

    @abstractmethod
    def get_timeline(
        self, campaign_id: str, db: Session
    ) -> list[CampaignTimelineResponse]:
        pass
