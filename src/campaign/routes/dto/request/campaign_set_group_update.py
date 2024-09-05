from pydantic import BaseModel

from src.campaign.domain.campaign import Campaign
from src.campaign.routes.dto.response.campaign_response import CampaignSetGroup


class CampaignSetGroupUpdate(BaseModel):
    base: Campaign
    set_group_list: list[CampaignSetGroup]
