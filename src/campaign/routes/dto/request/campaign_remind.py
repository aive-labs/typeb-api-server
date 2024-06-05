
from src.campaign.enums.campaign_media import CampaignMediaEnum
from src.core.database import BaseModel


class CampaignRemind(BaseModel):
    remind_step: int
    remind_media: CampaignMediaEnum | None = None
    remind_duration: int
