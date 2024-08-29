from pydantic import BaseModel


class AlreadySentCampaign(BaseModel):
    campaign_id: str
    msg_category: str | None = None
    remind_step: int | None = None
