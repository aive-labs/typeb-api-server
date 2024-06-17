from datetime import datetime

from pydantic import BaseModel

from src.audiences.enums.audience_create_type import AudienceCreateType
from src.audiences.routes.dto.response.audiences import RepresentativeItems


class AudienceCountTrend(BaseModel):
    name: str
    audience: dict
    net_audience: dict


class AudienceStats(BaseModel):
    audience_count: int | None = None
    audience_count_gap: int | None = None
    audience_portion: float
    audience_portion_gap: float
    audience_unit_price: float
    audience_unit_price_gap: float
    audience_trend: AudienceCountTrend
    excluded_audience_info: list


class AudienceSummary(BaseModel):
    revenue_per_audience: int
    purchase_per_audience: int
    revenue_per_purchase: int
    avg_pur_item_count: float
    retention_rate_3m: float
    response_rate: float
    created_at: datetime
    stat_updated_at: str
    agg_period: dict
    rep_list: list[RepresentativeItems] | None = None
    created_by_name: str  # 생성자
    owned_by_dept_name: str | None  # 생성부서
    owned_by_dept_abb_name: str | None  # 생성부서 약어
    create_type_code: AudienceCreateType  # 생성방법


class AudienceStatsInfo(BaseModel):
    audience_id: str
    audience_name: str
    audience_type_code: str
    audience_type_name: str
    description: list | None = None
    audience_stat: AudienceStats
    audience_summary: AudienceSummary

    class Config:
        from_attributes = True
