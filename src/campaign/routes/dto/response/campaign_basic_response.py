from pydantic import BaseModel

from src.campaign.domain.campaign import Campaign


class RecipientSummary(BaseModel):
    recipient_portion: float
    recipient_descriptions: list[str] | None = []


class CampaignBasicResponse(BaseModel):
    progress: str
    base: Campaign
    set_summary: RecipientSummary
    set_list: list | None = None
    set_group_list: list | None = None
    set_group_message_list: dict | None = None
