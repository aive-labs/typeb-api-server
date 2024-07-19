from abc import ABC, abstractmethod

from sqlalchemy.orm import Session

from src.campaign.routes.dto.response.campaign_summary_response import (
    CampaignSummaryResponse,
)


class CreateCampaignSummaryUseCase(ABC):

    @abstractmethod
    def create_campaign_summary(self, campaign_id: str, db: Session) -> CampaignSummaryResponse:
        pass
