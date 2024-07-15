from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from src.campaign.domain.campaign_remind import CampaignRemind
from src.common.utils.date_utils import localtime_converter


class Campaign(BaseModel):
    campaign_id: str | None = None
    campaign_name: str
    campaign_group_id: str | None = Field(None, alias="campaign_group_id")
    budget: int | None
    campaign_type_code: str
    campaign_type_name: str
    medias: str
    campaign_status_group_code: str
    campaign_status_group_name: str
    campaign_status_code: str
    campaign_status_name: str
    send_type_code: str
    send_type_name: str
    repeat_type: str | None
    week_days: str | None
    send_date: str | None
    is_msg_creation_recurred: bool
    is_approval_recurred: bool
    datetosend: Literal["end_of_month"] | int | str | None = None
    timetosend: str
    start_date: str | None
    end_date: str | None
    group_end_date: str | None
    has_remind: bool
    campaigns_exc: list[str] | None
    audiences_exc: list[str] | None
    strategy_id: str | None
    strategy_theme_ids: list[int] | None
    is_personalized: bool
    progress: str
    msg_delivery_vendor: str
    shop_send_yn: str
    retention_day: int | None = None
    remind_list: list[CampaignRemind] = []
    owned_by_dept: str
    owned_by_dept_name: str
    owned_by_dept_abb_name: str
    created_at: datetime = Field(default_factory=localtime_converter)
    created_by: str
    created_by_name: str
    updated_at: datetime = Field(default_factory=localtime_converter)
    updated_by: str

    model_config = ConfigDict(from_attributes=True)
