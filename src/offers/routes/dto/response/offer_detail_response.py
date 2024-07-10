from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel

from src.offers.domain.offer import Offer
from src.offers.enums.available_period_type import AvailablePeriodType
from src.offers.enums.available_scope import AvailableScope


class OfferDetailResponse(BaseModel):
    coupon_no: str
    coupon_name: str
    coupon_type: Optional[str] = None
    coupon_description: Optional[str] = None

    available_scope: Optional[str] = None
    available_scope_name: Optional[str] = None
    available_begin_datetime: Optional[str] = None
    available_end_datetime: Optional[str] = None
    available_product_list: Optional[List] = []
    available_category_list: Optional[List] = []

    available_period_type: Optional[str] = None
    available_period_type_name: Optional[str] = None
    available_day_from_issued: Optional[int] = None

    benefit_type: Optional[str] = None
    benefit_type_name: Optional[str] = None
    benefit_text: Optional[str] = None
    benefit_price: Optional[str] = None
    benefit_percentage: Optional[str] = None
    benefit_percentage_round_unit: Optional[str] = None
    benefit_percentage_max_price: Optional[str] = None
    include_regional_shipping_rate: Optional[str] = None  # TF
    include_foreign_delivery: Optional[str] = None  # TF

    issue_reserved: Optional[str] = None  # TF
    is_available: Optional[bool] = False

    coupon_created_at: datetime

    @staticmethod
    def from_model(model: Offer):
        return OfferDetailResponse(
            coupon_no=model.coupon_no,
            coupon_name=model.coupon_name,
            coupon_type=model.coupon_type,
            coupon_description=model.coupon_description,
            available_scope=model.available_scope,
            available_scope_name=(
                AvailableScope[model.available_scope].value
                if model.available_scope
                else None
            ),
            available_period_type=model.available_period_type,
            available_period_type_name=(
                AvailablePeriodType[model.available_period_type].value
                if model.available_period_type
                else None
            ),
            available_day_from_issued=model.available_day_from_issued,
            available_begin_datetime=model.available_begin_datetime,
            available_end_datetime=model.available_end_datetime,
            available_product_list=model.available_product_list,
            available_category_list=model.available_category_list,
            benefit_type=model.benefit_type,
            benefit_type_name=model.benefit_type_name,
            benefit_text=model.benefit_text,
            benefit_price=model.benefit_price,
            benefit_percentage=model.benefit_percentage,
            benefit_percentage_round_unit=model.benefit_percentage_round_unit,
            benefit_percentage_max_price=model.benefit_percentage_max_price,
            include_regional_shipping_rate=model.include_regional_shipping_rate,
            include_foreign_delivery=model.include_foreign_delivery,
            issue_reserved=model.issue_reserved,
            is_available=model.is_available,
            coupon_created_at=model.coupon_created_at,
        )
