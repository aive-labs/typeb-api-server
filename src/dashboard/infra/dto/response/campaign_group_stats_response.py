from pydantic import BaseModel


class CampaignGroupStatsResponse(BaseModel):

    campaign_id: str
    campaign_name: str  # 캠페인명
    group_code_lv1: str | int | None = None  ##필터컬럼1
    group_name_lv1: str | int | None = None  ##필터컬럼1
    group_code_lv2: str | None = None  ##필터컬럼2
    group_name_lv2: str | None = None  ##필터컬럼2
    recipient_count: int | None = None  ##타겟고객수(명)
    sent_cust_count: int | None = None  ##발송고객수(명)
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
