from datetime import datetime

from sqlalchemy import Column, DateTime, String

from src.core.database import BaseModel as Base


class ChannelMasterEntity(Base):
    __tablename__ = "channel_master"

    br_div = Column(String(5), primary_key=True, nullable=False)
    comp_cd = Column(String(4), primary_key=True, nullable=False)
    shop_cd = Column(String(6), primary_key=True, nullable=False)
    shop_nm = Column(String(50))
    re_shop_cd2 = Column(String(10))
    addr = Column(String(80))
    shop_tp2 = Column(String(2))
    shop_tp2_nm = Column(String(200))
    shop_tp4 = Column(String(5))
    shop_tp4_nm = Column(String(200))
    shop_tp5 = Column(String(5))
    shop_tp5_nm = Column(String(200))
    shop_mng_gb = Column(String(5))
    shop_mng_gb_nm = Column(String(200))
    team_cd = Column(String(5))
    team_nm = Column(String(200))
    shop_tp = Column(String(5))
    shop_tp_nm = Column(String(200))
    shop_stat = Column(String(5))
    shop_stat_nm = Column(String(200))
    open_dt = Column(String(8))
    close_dt = Column(String(8))
    area_cd = Column(String(5))
    area_nm = Column(String(200))
    tel_no1 = Column(String(5))
    tel_no2 = Column(String(5))
    tel_no3 = Column(String(5))
    zip_cd = Column(String(7))
    addr2 = Column(String(80))
    etl_time = Column(DateTime(timezone=True), default=datetime.now())
