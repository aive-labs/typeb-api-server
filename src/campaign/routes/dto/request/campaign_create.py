from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field

from src.campaign.enums.campaign_type import CampaignTypeEnum
from src.campaign.enums.repeat_type import RepeatType
from src.campaign.enums.send_type import SendtypeEnum
from src.campaign.routes.dto.request.campaign_remind import CampaignRemind
from src.common.enums.message_delivery_vendor import MsgDeliveryVendorEnum
from src.common.utils import localtime_converter


class CampaignCreate(BaseModel):
    campaign_name: str
    budget: int | None = None
    campaign_type_code: CampaignTypeEnum
    audience_type_code: str | None = None
    medias: str
    send_type_code: SendtypeEnum
    repeat_type: RepeatType | None = None
    week_days: str | None = None
    send_date: str | None = None
    is_msg_creation_recurred: bool
    is_approval_recurred: bool
    datetosend: Literal["end_of_month"] | int | None = None
    timetosend: str
    start_date: str | None = None
    end_date: str | None = None
    group_end_date: str | None = None
    has_remind: bool
    remind_list: list[CampaignRemind] | None = None
    strategy_id: str | None = None
    campaign_theme_ids: list[int] | None = None
    is_personalized: bool
    msg_delivery_vendor: MsgDeliveryVendorEnum
    retention_day: int | None = None  # 유지기간
    campaigns_exc: list[str] | None = None
    audiences_exc: list[str] | None = None
    created_at: datetime = Field(default_factory=localtime_converter)
    updated_at: datetime = Field(default_factory=localtime_converter)
