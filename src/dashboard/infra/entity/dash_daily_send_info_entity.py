from sqlalchemy import Column, DateTime, Integer, String

from src.core.database import Base as Base


class DashDailySendInfoEntity(Base):
    __tablename__ = "dash_daily_send_info"

    seq = Column(String, primary_key=True)
    campaign_id = Column(String(10))
    campaign_name = Column(String)
    start_date = Column(String)
    end_date = Column(String)
    campaign_status_name = Column(String)
    strategy_id = Column(String)
    strategy_name = Column(String)
    strategy_theme_id = Column(Integer)
    strategy_theme_name = Column(String)
    group_sort_num = Column(Integer)
    audience_id = Column(String)
    audience_name = Column(String)
    coupon_no = Column(String)
    coupon_name = Column(String)
    media = Column(String)
    cust_grade1 = Column(String)
    cust_grade1_nm = Column(String)
    age_group_10 = Column(String)
    cv_lv2 = Column(String)
    tot_recipient_count = Column(Integer)
    tot_success_count = Column(Integer)
    tot_send_cost = Column(Integer)
    etl_time = Column(DateTime(timezone=True))
