from abc import ABC, abstractmethod

from sqlalchemy.orm import Session

from src.campaign.model.request.campaign_set_group_message_request import (
    CampaignSetGroupMessageRequest,
)
from src.campaign.model.request.campaign_set_group_update import (
    CampaignSetGroupUpdate,
)
from src.campaign.model.response.campaign_set_group_update_response import (
    CampaignSetGroupUpdateResponse,
)
from src.campaign.model.response.update_campaign_set_group_message_response import (
    UpdateCampaignSetGroupMessageResponse,
)
from src.main.transactional import transactional
from src.user.domain.user import User


class UpdateCampaignSetMessageGroupUseCase(ABC):

    @transactional
    @abstractmethod
    def update_campaign_set_message_group(
        self,
        campaign_id: str,
        set_seq: int,
        set_group_message_updated: CampaignSetGroupUpdate,
        user,
        db: Session,
    ) -> CampaignSetGroupUpdateResponse:
        pass

    @transactional
    @abstractmethod
    def update_campaign_set_messages_contents(
        self,
        campaign_id: str,
        set_group_msg_seq: int,
        set_group_message_update: CampaignSetGroupMessageRequest,
        user: User,
        db: Session,
    ) -> UpdateCampaignSetGroupMessageResponse:
        pass
