from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class CampaignRemind(BaseModel):
    remind_seq: int | None = None
    campaign_id: str | None = None
    send_type_code: str
    remind_media: str | None = None
    remind_step: int
    remind_date: str
    remind_duration: int
    created_at: Optional[datetime] = None
    created_by: str
    updated_at: Optional[datetime] = None
    updated_by: str

    class Config:
        from_attributes = True
