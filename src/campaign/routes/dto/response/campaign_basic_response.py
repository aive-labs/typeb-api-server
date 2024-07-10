from pydantic import BaseModel

from src.campaign.domain.campaign import Campaign


class RecipientSummary(BaseModel):
    recipient_portion: str
    recipient_descriptions: str


class CampaignBasicResponse(BaseModel):
    progress: str
    base: Campaign
    set_summary: RecipientSummary
    set_list: list[str]
    set_group_list: list[str]
    set_group_message_list: list[str]
