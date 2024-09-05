from sqlalchemy import Column, DateTime, Integer, String

from src.core.database import Base as Base


class DashEndTableEntity(Base):
    __tablename__ = "dash_end_table"

    sale_dt = Column(String, primary_key=True)
    campaign_id = Column(String(10), primary_key=True)
    campaign_name = Column(String)
    start_date = Column(String)
    end_date = Column(String)
    campaign_status_name = Column(String)
    campaign_group_id = Column(String)
    strategy_id = Column(String)
    strategy_name = Column(String)
    strategy_theme_id = Column(Integer, primary_key=True)
    strategy_theme_name = Column(String)
    audience_id = Column(String, primary_key=True)
    audience_name = Column(String)
    coupon_no = Column(String)
    coupon_name = Column(String)
    media = Column(String, primary_key=True)
    cus_cd = Column(String, primary_key=True)
    group_sort_num = Column(Integer, primary_key=True)
    recp_no = Column(String, primary_key=True)
    order_item_code = Column(Integer, primary_key=True)
    cust_grade1 = Column(String)
    cust_grade1_nm = Column(String)
    age_group_10 = Column(String)
    cv_lv2 = Column(String)
    order_coupon_no = Column(String)
    coupon_usage = Column(Integer)
    category_name = Column(String)
    rep_nm = Column(String)
    product_name = Column(String)
    sale_amt = Column(Integer)
    sale_qty = Column(Integer)
    etl_time = Column(DateTime(timezone=True))
