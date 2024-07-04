from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class SendReservation(BaseModel):
    send_resv_seq: int
    set_group_msg_seq: int | None = None
    campaign_id: str
    campaign_name: str | None = None
    send_resv_date: datetime | None
    send_resv_state: str
    send_rslt_date: datetime | None
    send_rslt_state: str | None = None
    phone_send: str
    phone_callback: str
    send_sv_type: str
    send_msg_type: str
    send_msg_subject: str | None = None
    send_msg_body: str | None = None
    send_filecount: int | None = None
    send_filepath: str | None = None
    kko_yellowid: str | None = None
    kko_template_key: str | None = None
    kko_button_json: str | None = None
    kko_ft_subject: str | None = None
    kko_ft_adflag: str | None = None
    kko_ft_wideimg: str | None = None
    kko_at_type: str | None = None
    kko_at_item_json: str | None = None
    kko_at_accent: str | None = None
    kko_at_price: int | None = None
    kko_at_currency: str | None = None
    kko_send_timeout: int | None = None
    kko_ssg_retry: int = 0
    kko_resend_type: str | None = None
    kko_resend_msg: str | None = None
    cus_cd: str | None = None
    msg_category: str | None = None
    remind_step: int | None = None
    sent_success: str | None = None
    shop_cd: str | None = None
    shop_send_yn: str
    test_send_yn: str | None = None
    audience_id: str | None = None
    event_no: str | None = None
    create_resv_date: datetime | None
    create_resv_user: str
    update_resv_date: datetime | None
    update_resv_user: str

    class Config:
        from_attributes = True