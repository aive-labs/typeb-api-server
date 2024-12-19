from pydantic import BaseModel


class CampaignSetMessageUseRequest(BaseModel):
    is_used: bool
