from sqlalchemy import Column, String

from src.main.database import Base as Base


class CustomerPromotionMasterEntity(Base):
    __tablename__ = "cus_promotion_master"

    cus_cd = Column(String, primary_key=True, nullable=False)
    campaign_strategy_id = Column(String, nullable=True)
    campaign_strategy_name = Column(String, nullable=True)
    strategy_theme_id = Column(String, nullable=True)
    campaign_theme_name = Column(String, nullable=True)
    campaign_id = Column(String, primary_key=True, nullable=False)
    campaign_name = Column(String, nullable=True)
    campaign_type_code = Column(String, nullable=True)
    recommend_rep_nm = Column(String, nullable=True)
    audience_id = Column(String, primary_key=True, nullable=False)
    audience_name = Column(String, nullable=True)
    coupon_no = Column(String, nullable=True)
    coupon_name = Column(String, nullable=True)
    offer_type = Column(String, nullable=True)
    start_dt = Column(String, nullable=True)
    end_dt = Column(String, nullable=True)
    send_dt = Column(String, primary_key=True, nullable=False)
    response_yn = Column(String, nullable=True)
    response_dt = Column(String, nullable=True)
    use_offer_yn = Column(String, nullable=True)
    use_offer_dt = Column(String, nullable=True)
    recommend_purchase_yn = Column(String, nullable=True)
    recommend_purchase_dt = Column(String, nullable=True)
