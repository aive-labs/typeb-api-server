from pydantic import BaseModel

from src.common.enums.campaign_media import CampaignMedia


class CampaignRemindCreate(BaseModel):
    remind_step: int
    remind_media: CampaignMedia | None = None
    remind_duration: int
