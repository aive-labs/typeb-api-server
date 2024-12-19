from pydantic import BaseModel


class CampaignRemind(BaseModel):
    send_type_code: str
    remind_step: int
    remind_media: str | None = None
    remind_date: str
    remind_duration: int
    created_by: str
    updated_by: str
