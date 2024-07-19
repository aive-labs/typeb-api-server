from sqlalchemy import func
from sqlalchemy.orm import Session
from sqlalchemy.sql.functions import coalesce

from src.offers.infra.entity.offers_entity import OffersEntity


def get_coupons_by_ids(coupon_no_list: list, db: Session):
    return (
        db.query(
            OffersEntity.coupon_no,
            OffersEntity.coupon_name,
            OffersEntity.coupon_no.label("event_no"),
            OffersEntity.benefit_type,
            OffersEntity.benefit_type_name,
            func.min(coalesce(OffersEntity.benefit_price, OffersEntity.benefit_percentage)).label(
                "offer_amount"
            ),
        )
        .group_by(OffersEntity.coupon_no)
        .filter(OffersEntity.coupon_no.in_(coupon_no_list))
    )
