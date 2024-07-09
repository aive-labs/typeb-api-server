from datetime import datetime

from sqlalchemy import JSON, Boolean, Column, DateTime, Integer, String
from sqlalchemy.orm import relationship

from src.core.database import Base
from src.offers.infra.entity.offer_details_entity import OfferDetailsEntity


class OffersEntity(Base):
    __tablename__ = "offers"

    offer_key = Column(Integer, primary_key=True, index=True, autoincrement=True)
    offer_id = Column(String(32))
    coupon_no = Column(String, nullable=False)
    coupon_name = Column(String, nullable=False)
    coupon_type = Column(String, nullable=False)
    coupon_description = Column(String, nullable=False)
    benefit_type = Column(String, nullable=False)
    benefit_type_name = Column(String, nullable=False)

    comp_cd = Column(String(4), nullable=False)
    br_div = Column(String(5), nullable=False)
    offer_name = Column(String(1000))
    event_remark = Column(String(4000))
    crm_event_remark = Column(String(1000))
    sty_alert1 = Column(String(500))
    offer_type_code = Column(String(2))
    offer_type_name = Column(String(20))

    is_available = Column(Boolean, default=False)
    available_scope = Column(String)
    available_product_list = Column(JSON)
    available_category_list = Column(JSON)

    mileage_str_dt = Column(String(20))
    mileage_end_dt = Column(String(20))

    issue_max_count_by_user = Column(Integer)

    available_begin_datetime = Column(String)
    available_end_datetime = Column(String)

    created_at = Column(DateTime(timezone=True), default=datetime.now())
    created_by = Column(String, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=datetime.now())
    updated_by = Column(String, nullable=False)

    cus_data_batch_yn = Column(String(1))
    offer_source = Column(String(10))
    campaign_id = Column(String)

    shop_id = Column(String)
    issue_type = Column(String)
    issue_sub_type = Column(String)
    issued_flag = Column(String)
    deleted = Column(String)
    issue_order_path = Column(String)
    issue_order_type = Column(String)
    issue_reserved = Column(String)
    available_period_type = Column(String)
    available_site = Column(String)
    available_price_type = Column(String)

    is_stopped_issued_coupon = Column(String)
    benefit_text = Column(String)
    benefit_price = Column(String)
    benefit_percentage = Column(String)
    benefit_percentage_round_unit = Column(String)
    benefit_percentage_max_price = Column(String)
    coupon_direct_url = Column(String)
    available_date = Column(String)
    available_order_price_type = Column(String)
    available_min_price = Column(String)
    available_amount_type = Column(String)
    send_sms_for_issue = Column(String)
    issue_order_start_date = Column(String)
    issue_order_end_date = Column(String)

    offer_detail_options = relationship(
        OfferDetailsEntity, backref="offers", lazy=True, cascade="all, delete-orphan"
    )
