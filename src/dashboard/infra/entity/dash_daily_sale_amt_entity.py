from sqlalchemy import Column, DateTime, Integer, String

from src.core.database import Base as Base


class DashDailySaleAmtEntity(Base):
    __tablename__ = "dash_daily_sale_amt"

    sale_dt = Column(String, primary_key=True)
    tot_cust_count = Column(Integer)
    tot_sale_amt = Column(Integer)
    etl_time = Column(DateTime(timezone=True))
