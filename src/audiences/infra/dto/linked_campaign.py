from pydantic import BaseModel


class LinkedCampaign(BaseModel):
    audience_id: str
    campaign_status_code: str
