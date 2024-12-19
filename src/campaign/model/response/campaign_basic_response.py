from typing import List, Optional

from pydantic import BaseModel

from src.campaign.domain.campaign import Campaign
from src.campaign.model.response.campaign_response import (
    CampaignSet,
    CampaignSetGroup,
)
from src.campaign.model.response.campaign_reviewer import CampaignReviewer


class RecipientSummary(BaseModel):
    recipient_portion: float
    recipient_descriptions: list[str] | None = []


class CampaignBasicResponse(BaseModel):
    progress: str
    base: Campaign
    set_summary: RecipientSummary
    set_list: Optional[List[CampaignSet]] = None
    set_group_list: Optional[List[CampaignSetGroup]] = None
    set_group_message_list: Optional[dict] = None  # key(int), value(List[SetGroupMessage])
    reviewers: Optional[List[CampaignReviewer]] = []
