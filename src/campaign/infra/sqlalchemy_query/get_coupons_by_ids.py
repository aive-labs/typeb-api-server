from sqlalchemy import func
from sqlalchemy.orm import Session
from sqlalchemy.sql.functions import coalesce

from src.offers.infra.entity.offers_entity import OffersEntity


def get_coupons_by_ids(db: Session, offer_ids: list):
    return db.query(
        OffersEntity.coupon_no,
        OffersEntity.coupon_name,
        OffersEntity.coupon_no,
        OffersEntity.benefit_type,
        OffersEntity.benefit_type_name,
        func.min(coalesce(OffersEntity.benefit_price, OffersEntity.benefit_percentage)).label(
            "offer_amount"
        ),
    ).filter(OffersEntity.coupon_no.in_(offer_ids))
