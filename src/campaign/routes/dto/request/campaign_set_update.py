from typing import Optional, Union

from pydantic import BaseModel


class CampaignSetUpdateDetail(BaseModel):
    set_seq: Optional[int] = None
    set_sort_num: int
    is_group_added: Optional[bool] = None
    campaign_theme_id: Optional[int] = None
    campaign_theme_name: Optional[str] = None
    recsys_model_id: Optional[int] = None
    audience_id: str
    audience_name: str
    rep_nm_list: Optional[list[Union[str, None]]] = None
    offer_id: Optional[str] = None
    offer_name: Optional[str] = None
    medias: Optional[str] = None


class CampaignSetUpdate(BaseModel):
    set_list: list[CampaignSetUpdateDetail] | None = None
