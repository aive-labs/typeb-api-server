from pydantic import BaseModel


class CampaignRemindResponse(BaseModel):
    remind_step: int
    remind_media: str | None = None
    remind_duration: int
