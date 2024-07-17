from abc import ABC, abstractmethod

from sqlalchemy.orm import Session

from src.campaign.routes.dto.request.campaign_set_group_update import (
    CampaignSetGroupUpdate,
)
from src.campaign.routes.dto.response.campaign_set_group_update_response import (
    CampaignSetGroupUpdateResponse,
)
from src.core.transactional import transactional


class UpdateCampaignSetMessageGroupUseCase(ABC):

    @transactional
    @abstractmethod
    def exec(
        self,
        campaign_id: str,
        set_seq: int,
        set_group_message_updated: CampaignSetGroupUpdate,
        user,
        db: Session,
    ) -> CampaignSetGroupUpdateResponse:
        pass
