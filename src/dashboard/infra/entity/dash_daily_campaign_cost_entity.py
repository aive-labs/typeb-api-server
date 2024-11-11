from sqlalchemy import (
    TIMESTAMP,
    Column,
    Float,
    PrimaryKeyConstraint,
    String,
    Text,
)

from src.core.database import Base


class DashDailyCampaignCost(Base):
    __tablename__ = "dash_daily_campaign_cost"
    __table_args__ = {
        "primary_key": PrimaryKeyConstraint(
            "campaign_id", "cus_cd", name="dash_daily_campaign_cost_pkey"
        ),
        "schema": "aivelabs_sv",
    }

    cus_cd = Column(String, primary_key=True, nullable=False)
    campaign_id = Column(String(10), primary_key=True, nullable=False)
    send_resv_date = Column(TIMESTAMP(timezone=True), nullable=True)
    sent_success = Column(Text, nullable=True)
    media = Column(Text, nullable=True)
    cost_per_send = Column(Float, nullable=True)
    etltime = Column(TIMESTAMP(timezone=True), nullable=True)
