from typing import Optional, Union

from pydantic import BaseModel, model_validator


class CampaignSetUpdateDetail(BaseModel):
    set_seq: Optional[int] = None
    set_sort_num: int
    is_group_added: Optional[bool] = None
    strategy_theme_id: Optional[int] = None
    strategy_theme_name: Optional[str] = None
    recsys_model_id: Optional[int] = None
    audience_id: str
    audience_name: str
    rep_nm_list: Optional[list[Union[str, None]]] = None
    coupon_no: Optional[str] = None
    coupon_name: Optional[str] = None
    medias: Optional[str] = None

    @model_validator(mode="before")  # pyright: ignore [reportArgumentType]
    @classmethod
    def replace_changed_field(cls, values):
        if "campaign_theme_id" in values:
            values["strategy_theme_id"] = values.pop("campaign_theme_id")

        if "campaign_theme_name" in values:
            values["strategy_theme_name"] = values.pop("campaign_theme_name")

        if "offer_id" in values:
            values["coupon_no"] = values.pop("offer_id")

        if "offer_name" in values:
            values["coupon_name"] = values.pop("offer_name")

        return values


class CampaignSetUpdate(BaseModel):
    set_list: list[CampaignSetUpdateDetail] | None = None
