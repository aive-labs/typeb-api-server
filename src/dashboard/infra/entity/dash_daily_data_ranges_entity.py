from sqlalchemy import (
    TIMESTAMP,
    Column,
    Integer,
    PrimaryKeyConstraint,
    String,
    Text,
)

from src.core.database import Base


class DashDailyDateRanges(Base):
    __tablename__ = "dash_daily_date_ranges"
    __table_args__ = {
        "schema": "aivelabs_sv",
        "primary_key": PrimaryKeyConstraint(
            "campaign_id",
            "audience_id",
            "media",
            "sale_dt",
            name="dash_daily_campaign_cost_pkey",
        ),
    }

    seq = Column(Text, nullable=True)
    sale_dt = Column(Text, primary_key=True, nullable=True)
    campaign_id = Column(String(10), primary_key=True, nullable=True)
    campaign_name = Column(Text, nullable=True)
    actual_start_date = Column(Text, nullable=True)
    send_date = Column(Text, nullable=True)
    start_date = Column(Text, nullable=True)
    end_date = Column(Text, nullable=True)
    campaign_status_name = Column(Text, nullable=True)
    group_sort_num = Column(Integer, nullable=True)
    strategy_theme_id = Column(Integer, nullable=True)
    strategy_theme_name = Column(Text, nullable=True)
    strategy_id = Column(String, nullable=True)
    strategy_name = Column(Text, nullable=True)
    audience_id = Column(String, primary_key=True, nullable=True)
    audience_name = Column(Text, nullable=True)
    coupon_no = Column(String, nullable=True)
    coupon_name = Column(Text, nullable=True)
    media = Column(Text, primary_key=True, nullable=True)
    etltime = Column(TIMESTAMP(timezone=True), nullable=True)
