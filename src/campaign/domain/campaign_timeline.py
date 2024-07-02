from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class CampaignTimeline(BaseModel):
    timeline_no: Optional[int] = None
    timeline_type: Optional[str] = None
    description: Optional[str] = None
    status_no: Optional[str] = None
    created_at: Optional[datetime] = None
    created_by: Optional[str] = None
    created_by_name: Optional[str] = None
    email: Optional[str] = None
    photo_uri: Optional[str] = None
    department_id: Optional[str] = None
    department_name: Optional[str] = None
    test_callback_number: Optional[str] = None

    class Config:
        from_attributes = True
