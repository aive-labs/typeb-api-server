from pydantic import BaseModel, ConfigDict


class CampaignAudienceStatsResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    campaign_id: str
    campaign_name: str
    start_date: str
    end_date: str
    strategy_theme_id: int | None = None
    strategy_theme_name: str | None = None
    audience_id: str
    audience_name: str
    recipient_count: int | None = None
    response_cust_count: int | None = None
    response_rate: float | None = None
    response_revenue: int | None = None
    response_roi: float | None = None
