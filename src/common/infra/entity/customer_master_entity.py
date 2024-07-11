from datetime import datetime

from sqlalchemy import Column, DateTime, Float, Integer, String

from src.core.database import Base


class CustomerMasterEntity(Base):
    __tablename__ = "customer_master"

    cus_cd = Column(String, primary_key=True, index=True)
    cust_name = Column(String)
    sex = Column(String)
    br_div = Column(String)
    team_cd = Column(String)
    join_dt = Column(String)
    main_shop = Column(String)
    quit_dt = Column(String)
    join_shop_code = Column(String)
    shop_nm = Column(String)
    addr = Column(String)
    birth = Column(String)
    solar_gb = Column(String)
    cus_div = Column(String)
    cus_div_nm = Column(String)
    cust_grade1 = Column(String)
    cus_grade1_nm = Column(String)
    rmk = Column(String)
    illegality_yn = Column(String)
    cust_status = Column(String)
    last_contact_dt = Column(String)
    remain_pnt = Column(Float)
    hp_no = Column(String)
    buy_shop_dt = Column(String)
    nepa_join_dt = Column(String)
    this_year_birthday = Column(String)
    on_join_yn = Column(String)
    on_user_stat = Column(String)
    on_withdraw_dt = Column(String)
    on_reg_dt = Column(String)
    on_user_no = Column(Integer)
    tot_mall_id = Column(String)
    sms_rcv_yn = Column(String)
    adver_rcv_yn_tm = Column(String)
    adver_rcv_yn_email = Column(String)
    adver_rcv_yn_dm = Column(String)
    cus_card_no = Column(String)
    track_id = Column(String)
    remain_point = Column(Integer)
    join_event_point = Column(String, nullable=True)
    etl_time = Column(DateTime(timezone=True), default=datetime.now())
