from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field, model_validator

from src.campaign.enums.campaign_type import CampaignType
from src.campaign.enums.repeat_type import RepeatTypeEnum
from src.campaign.enums.send_type import SendTypeEnum
from src.campaign.routes.dto.request.campaign_remind_create import CampaignRemindCreate
from src.common.enums.message_delivery_vendor import MsgDeliveryVendorEnum
from src.common.utils.date_utils import localtime_converter


class CampaignCreate(BaseModel):
    campaign_name: str
    budget: int | None = None
    campaign_type_code: CampaignType
    medias: str
    send_type_code: SendTypeEnum
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
    remind_list: list[CampaignRemindCreate] | None = None
    strategy_id: str | None = None
    strategy_theme_ids: list[int] | None = None
    is_personalized: bool
    msg_delivery_vendor: MsgDeliveryVendorEnum
    retention_day: int | None = None  # 유지기간
    campaigns_exc: list[str] | None = None
    audiences_exc: list[str] | None = None
    created_at: datetime = Field(default_factory=localtime_converter)
    updated_at: datetime = Field(default_factory=localtime_converter)

    @model_validator(mode="before")  # pyright: ignore [reportArgumentType]
    @classmethod
    def replace_changed_field(cls, values):
        if "campaign_theme_id" in values:
            values["strategy_theme_id"] = values.pop("campaign_theme_id")

        if "campaign_theme_name" in values:
            values["strategy_theme_name"] = values.pop("campaign_theme_name")

        if "campaign_theme_ids" in values:
            values["strategy_theme_ids"] = values.pop("campaign_theme_ids")

        return values
