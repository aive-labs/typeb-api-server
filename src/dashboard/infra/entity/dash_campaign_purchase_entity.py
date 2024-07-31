from sqlalchemy import Column, DateTime, Integer, String

from src.core.database import Base as Base


class DashCampaignPurchaseEntity(Base):
    __tablename__ = "dash_campaign_purchase"

    campaign_id = Column(String(10), primary_key=True)
    campaign_name = Column(String)
    campaign_start_date = Column(String)
    campaign_end_date = Column(String)
    cus_cd = Column(String, primary_key=True)
    tot_sale_amt = Column(Integer)
    tot_sale_qty = Column(Integer)
    purchase_times = Column(Integer)
    purchase_days = Column(Integer)
    first_sale_dt = Column(String)
    last_sale_dt = Column(String)
    etl_time = Column(DateTime)
