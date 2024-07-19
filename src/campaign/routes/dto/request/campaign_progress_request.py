from pydantic import BaseModel

from src.campaign.enums.campaign_progress import CampaignProgress


class CampaignProgressRequest(BaseModel):
    progress: CampaignProgress
