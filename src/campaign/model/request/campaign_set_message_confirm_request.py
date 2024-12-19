from pydantic import BaseModel


class CampaignSetMessageConfirmReqeust(BaseModel):
    is_confirmed: bool
