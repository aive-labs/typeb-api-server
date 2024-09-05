from abc import ABC, abstractmethod

from sqlalchemy.orm import Session

from src.campaign.routes.dto.response.campaign_set_description_response import (
    CampaignSetDescriptionResponse,
)


class GetCampaignSetDescriptionUseCase(ABC):

    @abstractmethod
    def exec(self, campaign_id: str, db: Session) -> CampaignSetDescriptionResponse:
        pass
