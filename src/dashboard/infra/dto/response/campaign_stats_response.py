from pydantic import BaseModel, ConfigDict


class CampaignStatsResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    campaign_id: str
    campaign_name: str  ## 캠페인명
    campaign_theme_id: int | None = None
    campaign_theme_name: str | None = None  # 테마명
    audience_id: str | None = None
    audience_name: str | None = None  ## 타겟
    offer_id: str | None = None
    offer_name: str | None = None  ##오퍼
    media: str | None = None  ##매체 (property명 바뀔수있음)
    recipient_count: int | None = None  ##발송고객(명)
    sent_cust_count: int | None = None  ##발송성공고객(명)
    media_cost: int | None = None  ##발송비용
    response_cust_count: int | None = None  ##전환고객(명)
    response_rate: float | None = None  # 전환율(%)
    response_quantity: int | None = None  ##반응판매수량
    response_revenue: int | None = None  ##반응매출액
    response_unit_price: int | None = None  ##객단가
    response_roi: float | None = None  ##ROI
    e_response_cust_count: int | None = None  ##전환고객(명)
    e_response_rate: float | None = None  # 전환율(%)
    e_response_quantity: int | None = None  ##반응판매수량
    e_response_revenue: int | None = None  ##반응매출액
    e_response_unit_price: int | None = None  ##객단가
