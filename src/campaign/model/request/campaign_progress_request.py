from pydantic import BaseModel

from src.campaign.model.campaign_progress import CampaignProgress


class CampaignProgressRequest(BaseModel):
    progress: CampaignProgress
