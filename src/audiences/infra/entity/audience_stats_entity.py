from sqlalchemy import Column, Float, Integer, String

from src.core.database import BaseModel as Base


class AudienceStatsEntity(Base):
    __tablename__ = "audience_stats"

    audience_id = Column(String, primary_key=True, index=True)
    audience_type_code = Column(String, nullable=False)
    audience_count = Column(Integer, nullable=False)
    audience_count_gap = Column(Integer, nullable=True)
    net_audience_count = Column(Integer)
    agg_period_start = Column(String, nullable=False)
    agg_period_end = Column(String, nullable=False)
    excluded_customer_count = Column(Integer, nullable=True)
    audience_portion = Column(Float, nullable=True)
    audience_portion_gap = Column(Float)
    audience_unit_price = Column(Float, nullable=True)
    audience_unit_price_gap = Column(Float)
    revenue_per_audience = Column(Integer, nullable=True)
    purchase_per_audience = Column(Integer, nullable=True)
    revenue_per_purchase = Column(Integer, nullable=True)
    avg_pur_item_count = Column(Float, nullable=True)
    retention_rate_3m = Column(Float, nullable=True)
    response_rate = Column(Float, nullable=True)
    stat_updated_at = Column(String, nullable=True)
