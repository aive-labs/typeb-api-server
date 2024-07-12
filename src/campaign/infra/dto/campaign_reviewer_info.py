from typing import Optional

from pydantic import BaseModel


class CampaignReviewerInfo(BaseModel):
    approval_no: int
    user_id: str
    user_name: str
    is_approved: bool
    department_abb_name: str
    test_callback_number: Optional[str]  # Assuming this can be None
    is_approved: bool

    class Config:
        from_attributes = True