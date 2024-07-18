from datetime import datetime
from typing import List, Literal

from pydantic import BaseModel, Field

from src.campaign.domain.campaign_remind import CampaignRemind
from src.campaign.enums.campagin_status import (
    CampaignStatusEnum,
    CampaignStatusGroupEnum,
)
from src.campaign.enums.campaign_progress import CampaignProgress
from src.campaign.enums.campaign_type import CampaignTypeEnum
from src.campaign.enums.repeat_type import RepeatTypeEnum
from src.campaign.enums.send_type import SendTypeEnum
from src.campaign.enums.set_group_category import SetGroupCategoryEnum
from src.common.enums.campaign_media import CampaignMedia
from src.common.enums.message_delivery_vendor import MsgDeliveryVendorEnum
from src.common.utils.date_utils import localtime_converter
from src.message_template.enums.message_type import MessageType


class CampaignBase(BaseModel):
    campaign_name: str
    budget: int | None = None
    campaign_type_code: CampaignTypeEnum
    campaign_type_name: str
    audience_type_code: str | None = None
    medias: str
    campaign_status_group_code: CampaignStatusGroupEnum
    campaign_status_group_name: str
    campaign_status_code: CampaignStatusEnum
    campaign_status_name: str
    send_type_code: SendTypeEnum
    send_type_name: str
    repeat_type: RepeatTypeEnum | None = None
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
    remind_list: List[CampaignRemind] | None = None
    strategy_id: str | None = None
    strategy_theme_ids: List[int] | None = None
    is_personalized: bool
    msg_delivery_vendor: MsgDeliveryVendorEnum
    campaigns_exc: List[str] | None = None
    audiences_exc: List[str] | None = None
    shop_send_yn: str
    retention_day: int | None = None
    owned_by_dept: str
    owned_by_dept_name: str | None = None
    owned_by_dept_abb_name: str | None = None
    progress: CampaignProgress
    created_at: datetime = Field(default_factory=localtime_converter)
    created_by: str | int | None = None
    created_by_name: str | None = None
    updated_at: datetime = Field(default_factory=localtime_converter)
    updated_by: str | int | None = None


class CampaignReadBase(CampaignBase):
    campaign_id: str
    campaign_group_id: str


class CampaignSetGroup(BaseModel):
    set_group_seq: int | None = None
    set_seq: int | None = None
    set_sort_num: int | None = None
    group_sort_num: int | None = None
    media: CampaignMedia | None = None
    msg_type: MessageType | None = None
    recipient_group_rate: float | None = None
    recipient_group_count: int | None = None
    set_group_category: SetGroupCategoryEnum | None = None
    set_group_val: str | None = None
    rep_nm: str | None = None
    contents_id: int | None = None
    contents_name: str | None = None


class CampaignSet(BaseModel):
    set_seq: int | None = None
    set_sort_num: int | None = None
    is_group_added: bool | None = None
    strategy_theme_id: int | None = None
    strategy_theme_name: str | None = None
    recsys_model_id: int | None = None
    audience_id: str | None = None
    audience_name: str | None = None
    audience_count: int | None = None
    audience_portion: float | None = None
    audience_unit_price: float | None = None
    response_rate: float | None = None
    rep_nm_list: List[str | None] | None = None
    coupon_no: str | None = None
    coupon_name: str | None = None
    recipient_count: int | None = None
    medias: str | None = None
    contents_names: List[str | None] | None = None
    is_confirmed: bool | None = None
    is_message_confirmed: bool | None = None
    media_cost: int | None = None
