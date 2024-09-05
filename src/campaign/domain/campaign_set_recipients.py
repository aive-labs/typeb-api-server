from datetime import datetime

from pydantic import BaseModel


class CampaignSetRecipients(BaseModel):
    set_recipient_seq: int | None = None
    campaign_id: str
    set_sort_num: int
    group_sort_num: int
    cus_cd: str
    set_group_category: str | None = None
    set_group_val: str | None = None
    rep_nm: str | None = None
    contents_id: int | None = None
    send_result: str | None = None
    created_at: datetime | None = None
    created_by: str
    updated_at: datetime | None = None
    updated_by: str

    class Config:
        orm_mode = True
