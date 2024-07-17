from typing import Optional, Union

from pydantic import BaseModel

from src.campaign.routes.dto.response.campaign_response import CampaignSetGroup


class CampaignSetResponse(BaseModel):
    set_seq: Optional[int] = None  # step2
    set_sort_num: Optional[int] = None
    is_group_added: Optional[bool] = None
    campaign_theme_id: Optional[int] = None
    campaign_theme_name: Optional[str] = None  # 기본 캠페인 optional
    recsys_model_id: Optional[int] = None
    audience_id: Optional[str] = None
    audience_name: Optional[str] = None
    audience_count: Optional[int] = None  # 기본 캠페인 optional
    audience_portion: Optional[float] = None  # 기본 캠페인 optional
    audience_unit_price: Optional[float] = None  # 기본 캠페인 optional
    response_rate: Optional[float] = None  # 기본 캠페인 optional
    rep_nm_list: Optional[list[Union[str, None]]] = None  # 수정 로그(1)
    offer_id: Optional[str] = None
    offer_name: Optional[str] = None
    recipient_count: Optional[int] = None
    medias: Optional[str] = None
    contents_names: Optional[list[Union[str, None]]] = None  # 수정 로그(9)
    is_confirmed: Optional[bool] = None  # step4 < 설정완료시
    is_message_confirmed: Optional[bool] = None  # step3 < 세트 메세지 확인 시
    media_cost: Optional[int] = None


class CampaignSetGroupUpdateResponse(BaseModel):
    campaign_set: CampaignSetResponse
    campaign_set_group_list: list[CampaignSetGroup]
