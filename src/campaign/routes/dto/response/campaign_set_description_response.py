from typing import Optional, Union

from pydantic import BaseModel


class CampaignSetDescription(BaseModel):
    set_seq: Optional[int] = None  # step2
    set_sort_num: Optional[int] = None
    strategy_theme_id: Optional[int] = None
    strategy_theme_name: Optional[str] = None
    audience_id: str
    audience_name: str
    audience_count: int
    audience_portion: float
    audience_unit_price: float
    response_rate: float
    coupon_no: Optional[str] = None
    coupon_name: Optional[str] = None
    recipient_count: int
    medias: Optional[str] = None
    contents_names: Optional[list[Union[str, None]]] = None  # 수정 로그(9)
    is_confirmed: Optional[bool] = None  # step4 < 설정완료시
    media_cost: Optional[int] = None


class CampaignSetDescriptionResponse(BaseModel):
    campaign_set: list[CampaignSetDescription]
