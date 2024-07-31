from datetime import datetime

from sqlalchemy import TIMESTAMP, BigInteger, Column, Date, DateTime, String

from src.core.database import Base


class CustomerMasterEntity(Base):
    __tablename__ = "customer_master"

    shop_no = Column(BigInteger)
    cus_cd = Column(String, primary_key=True)
    gender = Column(String)
    age = Column(String)
    group_no = Column(BigInteger)
    cust_grade1 = Column(String)
    cust_name = Column(String)
    nick_name = Column(String)
    hp_no = Column(String)
    phone = Column(String)
    email = Column(String)
    wedding_anniversary = Column(String)
    city = Column(String)
    state = Column(String)
    zipcode = Column(String)
    address1 = Column(String)
    address2 = Column(String)
    birthday = Column(TIMESTAMP(timezone=True))
    solar_calendar = Column(String)
    lifetime_member = Column(String)
    join_path = Column(String)
    sms = Column(String)
    news_mail = Column(String)
    member_authentification = Column(String)
    use_mobile_app = Column(String)
    use_blacklist = Column(String)
    blacklist_type = Column(String)
    total_points = Column(String)
    available_points = Column(String)
    used_points = Column(String)
    last_login_date = Column(Date)
    track_id = Column(String)
    created_date = Column(TIMESTAMP(timezone=True))
    etl_time = Column(DateTime, default=datetime.now())
