from typing import Optional

from pydantic import BaseModel


class CampaignSummaryResponse(BaseModel):
    campaign_type_code: str
    campaign_type_name: str
    send_type_code: str
    send_type_name: str
    total_reciepient: int
    budget: int
    repeat_type: Optional[str] = None
    week_days: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    send_date: Optional[str] = None
    campaign_status_code: str
    campaign_status_name: str
    msg_type_count: int
    msg_type_tup: list
    audience_count: int
    contents_count: int
    campaign_msg_resv_date: str | None = None
    remind_step1_resv_date: Optional[str] = None
    remind_step2_resv_date: Optional[str] = None
    remind_step3_resv_date: Optional[str] = None
