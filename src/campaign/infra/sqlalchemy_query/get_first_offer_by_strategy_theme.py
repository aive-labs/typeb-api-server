from sqlalchemy import func
from sqlalchemy.orm import Session
from sqlalchemy.sql.functions import coalesce

from src.offers.infra.entity.offers_entity import OffersEntity
from src.strategy.infra.entity.strategy_theme_offers_entity import (
    StrategyThemeOfferMappingEntity,
)


def get_first_offer_by_strategy_theme(strategy_theme_ids: list, db: Session):
    subquery = (
        db.query(
            StrategyThemeOfferMappingEntity.strategy_theme_id,
            func.first_value(StrategyThemeOfferMappingEntity.coupon_no)
            .over(
                partition_by=StrategyThemeOfferMappingEntity.strategy_theme_id,
                order_by=StrategyThemeOfferMappingEntity.updated_at,
            )
            .label("coupon_no"),
        )
        .distinct()
        .subquery()
    )

    result = db.query(
        StrategyThemeOfferMappingEntity.strategy_theme_id,
        StrategyThemeOfferMappingEntity.coupon_no,
        OffersEntity.coupon_name,
        OffersEntity.available_scope,
        func.min(coalesce(OffersEntity.benefit_price, OffersEntity.benefit_percentage))
        .join(
            subquery,
            (StrategyThemeOfferMappingEntity.strategy_theme_id == subquery.c.campaign_theme_id)
            & (StrategyThemeOfferMappingEntity.coupon_no == subquery.c.coupon_no),
        )
        .join(
            OffersEntity,
            StrategyThemeOfferMappingEntity.coupon_no == OffersEntity.coupon_no,
        ),
    )

    return result
