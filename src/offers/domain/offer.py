from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel

from src.offers.infra.entity.offers_entity import OffersEntity


class Offer(BaseModel):
    coupon_no: str
    coupon_name: str
    coupon_type: Optional[str] = None
    coupon_description: Optional[str] = None
    coupon_created_at: datetime
    benefit_type: Optional[str] = None
    benefit_type_name: Optional[str] = None
    comp_cd: Optional[str] = None
    br_div: Optional[str] = None
    is_available: Optional[bool] = False
    available_scope: Optional[str] = None
    available_product_list: Optional[List] = []
    available_category_list: Optional[List] = []
    issue_max_count_by_user: Optional[int] = None
    available_begin_datetime: Optional[str] = None
    available_end_datetime: Optional[str] = None
    campaign_id: Optional[str] = None
    shop_no: Optional[str] = None
    issue_type: Optional[str] = None
    issue_sub_type: Optional[str] = None
    issue_order_path: Optional[str] = None
    issue_order_type: Optional[str] = None
    issue_reserved: Optional[str] = None
    issue_reserved_date: Optional[str] = None
    available_period_type: Optional[str] = None
    available_day_from_issued: Optional[int] = None
    available_site: Optional[str] = None
    available_price_type: Optional[str] = None
    is_stopped_issued_coupon: Optional[str] = None
    benefit_text: Optional[str] = None
    benefit_price: Optional[str] = None
    benefit_percentage: Optional[str] = None
    benefit_percentage_round_unit: Optional[str] = None
    benefit_percentage_max_price: Optional[str] = None
    include_regional_shipping_rate: Optional[str] = None
    include_foreign_delivery: Optional[str] = None
    coupon_direct_url: Optional[str] = None
    available_date: Optional[str] = None
    available_order_price_type: Optional[str] = None
    available_min_price: Optional[str] = None
    available_amount_type: Optional[str] = None
    send_sms_for_issue: Optional[str] = None
    issue_order_start_date: Optional[str] = None
    issue_order_end_date: Optional[str] = None
    deleted: Optional[str] = None
    cus_data_batch_yn: Optional[str] = None
    offer_source: Optional[str] = None
    created_at: datetime
    created_by: str
    updated_at: datetime
    updated_by: str

    class Config:
        from_attributes = True

    @staticmethod
    def from_entity(entity: OffersEntity) -> "Offer":
        offer_data = {**{col.name: getattr(entity, col.name) for col in entity.__table__.columns}}
        return Offer.model_validate(offer_data)
