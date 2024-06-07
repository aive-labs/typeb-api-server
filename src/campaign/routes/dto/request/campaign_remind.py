from pydantic import BaseModel

from src.campaign.enums.campaign_media import CampaignMediaEnum


class CampaignRemind(BaseModel):
    remind_step: int
    remind_media: CampaignMediaEnum | None = None
    remind_duration: int
