from pydantic import BaseModel, ConfigDict


class CampaignSummaryStatsResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    campaign_id: str
    campaign_name: str  ## 캠페인명
    start_date: str | None = None  # 캠페인시작
    end_date: str | None = None  # 캠페인끝
    campaign_status_name: str | None = None  # 캠페인상태
    recipient_count: int | None = None  ##발송고객수(명)
    sent_cust_count: int | None = None  ##발송성공고객수(명)
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
