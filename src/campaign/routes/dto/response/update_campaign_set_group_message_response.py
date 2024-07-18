from pydantic import BaseModel

from src.campaign.domain.campaign_messages import Message


class UpdateCampaignSetGroupMessageResponse(BaseModel):
    set_group_msg_seq: int
    msg_obj: Message
