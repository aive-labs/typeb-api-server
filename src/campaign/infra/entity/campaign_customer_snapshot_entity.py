from sqlalchemy import (
    TIMESTAMP,
    BigInteger,
    Column,
    Integer,
    String,
)

from src.main.database import Base


class CampaignCustomerSnapshot(Base):
    __tablename__ = "campaign_customer_snapshot"
    __table_args__ = {"schema": "aivelabs_sv"}

    cus_cd = Column(String, primary_key=True, nullable=False)
    campaign_id = Column(String(10), primary_key=True, nullable=False)
    campaign_name = Column(String, nullable=False)
    send_date = Column(String, nullable=False)
    start_date = Column(String, nullable=False)
    end_date = Column(String, nullable=False)
    campaign_status_name = Column(String, nullable=True)
    campaign_group_id = Column(String, nullable=True)
    strategy_id = Column(String, nullable=True)
    strategy_name = Column(String, nullable=True)
    group_sort_num = Column(Integer, nullable=True)
    strategy_theme_id = Column(Integer, nullable=True)
    strategy_theme_name = Column(String, nullable=True)
    audience_id = Column(String, nullable=False)
    audience_name = Column(String, nullable=False)
    coupon_no = Column(String, nullable=True)
    coupon_name = Column(String, nullable=True)
    age_group_10 = Column(String, nullable=True)
    group_no = Column(BigInteger, nullable=True)
    group_name = Column(String, nullable=True)
    cv_lv2 = Column(String, nullable=True)
    recsys_model_id = Column(Integer, nullable=True)
    recsys_model_name = Column(String, nullable=True)
    etltime = Column(TIMESTAMP(timezone=True), nullable=True)
