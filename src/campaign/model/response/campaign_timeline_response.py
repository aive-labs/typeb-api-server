from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class StatusUserProfile(BaseModel):
    user_id: Optional[str] = None
    username: Optional[str] = None
    email: Optional[str] = None
    photo_uri: Optional[str] = None
    department_id: Optional[str] = None
    department_name: Optional[str] = None
    test_callback_number: Optional[str] = None


class CampaignTimelineResponse(BaseModel):
    timeline_no: Optional[int] = None
    timeline_type: Optional[str] = None
    description: Optional[str] = None
    status_no: Optional[str] = None
    created_at: Optional[datetime] = None
    created_by: StatusUserProfile
