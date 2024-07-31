from datetime import datetime

import pytz
from sqlalchemy import ARRAY, Boolean, Column, DateTime, Integer, String, text

from src.core.database import Base


class OffersEntity(Base):
    __tablename__ = "offers"

    coupon_no = Column(String, primary_key=True, index=True, nullable=False)
    coupon_name = Column(String, nullable=False)
    coupon_type = Column(String)
    coupon_description = Column(String)
    coupon_created_at = Column(String)
    benefit_type = Column(String)
    benefit_type_name = Column(String)
    comp_cd = Column(String)
    br_div = Column(String)
    is_available = Column(Boolean, default=False)
    available_scope = Column(String)
    available_product_list = Column(ARRAY(String), nullable=True)
    available_category_list = Column(ARRAY(String), nullable=True)
    issue_max_count_by_user = Column(Integer)
    available_begin_datetime = Column(String)
    available_end_datetime = Column(String)
    campaign_id = Column(String)
    shop_no = Column(String)
    issue_type = Column(String)
    issue_sub_type = Column(String)
    issue_order_path = Column(String)
    issue_order_type = Column(String)
    issue_reserved = Column(String)
    issue_reserved_date = Column(String)
    available_period_type = Column(String)
    available_day_from_issued = Column(Integer)
    available_site = Column(String)
    available_price_type = Column(String)
    is_stopped_issued_coupon = Column(String)
    benefit_text = Column(String)
    benefit_price = Column(String)
    benefit_percentage = Column(String)
    benefit_percentage_round_unit = Column(String)
    benefit_percentage_max_price = Column(String)
    include_regional_shipping_rate = Column(String)
    include_foreign_delivery = Column(String)
    coupon_direct_url = Column(String)
    available_date = Column(String)
    available_order_price_type = Column(String)
    available_min_price = Column(String)
    available_amount_type = Column(String)
    send_sms_for_issue = Column(String)
    issue_order_start_date = Column(String)
    issue_order_end_date = Column(String)
    deleted = Column(String)
    cus_data_batch_yn = Column(String(1))
    offer_source = Column(String(10))
    created_at = Column(
        DateTime,
        nullable=False,
        default=lambda: datetime.now(pytz.timezone("Asia/Seoul")),
    )
    created_by = Column(String, nullable=False, default=text("(user)"))
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(pytz.timezone("Asia/Seoul")),
        onupdate=datetime.now(),
    )
    updated_by = Column(String, nullable=False, default=text("(user)"))
