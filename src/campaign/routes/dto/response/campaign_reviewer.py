from typing import Optional

from pydantic import BaseModel


class CampaignReviewer(BaseModel):
    approval_no: int
    user_id: int
    user_name_object: str
    test_callback_number: Optional[str] = None
    is_approved: bool
