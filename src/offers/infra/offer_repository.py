from contextlib import AbstractContextManager
from datetime import datetime
from typing import Callable

from sqlalchemy import or_
from sqlalchemy.orm import Session

from src.common.timezone_setting import selected_timezone
from src.common.utils.string_utils import is_convertible_to_int
from src.core.exceptions.exceptions import NotFoundException
from src.offers.domain.cafe24_coupon import Cafe24CouponResponse
from src.offers.domain.offer import Offer
from src.offers.enums.cafe24_coupon_benefit_type import Cafe24CouponBenefitType
from src.offers.enums.offer_use_type import OfferUseType
from src.offers.infra.entity.offer_details_entity import OfferDetailsEntity
from src.offers.infra.entity.offers_entity import OffersEntity
from src.search.routes.dto.id_with_label_response import IdWithLabel
from src.strategy.infra.entity.strategy_theme_entity import StrategyThemesEntity
from src.strategy.infra.entity.strategy_theme_offers_entity import (
    StrategyThemeOfferMappingEntity,
)
from src.users.domain.user import User


class OfferRepository:
    def __init__(self, db: Callable[..., AbstractContextManager[Session]]):
        """_summary_

        Args:
            db (Callable[..., AbstractContextManager[Session]]):
            - Callable 호출 가능한 객체
            - AbstractContextManager[Session]: 세션 객체를 반환하는 컨텍스트 관리자
            - Session: SQLAlchemy의 세션 객체

        """
        self.db = db

    def get_all_offers(
        self, based_on, sort_by, start_date, end_date, keyword, db: Session
    ) -> list[Offer]:
        base_query = (
            db.query(OffersEntity)
            # .filter(
            #     and_(
            #         OffersEntity.available_end_datetime >= start_date,
            #         OffersEntity.available_begin_datetime <= end_date,
            #     )
            # )
            .order_by(OffersEntity.offer_source, OffersEntity.available_begin_datetime.desc())
        )

        if keyword:
            base_query = base_query.filter(
                or_(
                    OffersEntity.coupon_name.ilike(f"%{keyword}%"),
                    OffersEntity.coupon_no.ilike(f"%{keyword}%"),
                    OffersEntity.offer_source.ilike(f"%{keyword}%"),
                    OffersEntity.benefit_type_name.ilike(f"%{keyword}%"),
                )
            )

        offer_entities = base_query.all()
        use_type_dict = {v.value: v.description for _, v in OfferUseType.__members__.items()}

        offers = []
        for offer in offer_entities:
            temp_offer = Offer.model_validate(offer)
            temp_offer.available_scope = use_type_dict.get(temp_offer.available_scope, "")
            temp_offer.offer_source = temp_offer.offer_source if temp_offer.offer_source else ""

            offers.append(temp_offer)

        return offers

    def _create_label(self, data):
        return f"({data.id}) {data.name}"

    def get_search_offers_of_sets(
        self, strategy_id: str, keyword: str, user: User
    ) -> list[IdWithLabel]:
        with self.db() as db:

            condition = self._add_search_offer_condition_by_user(user)

            offer_ids = (
                db.query(StrategyThemeOfferMappingEntity.coupon_no)
                .join(
                    StrategyThemesEntity,
                    StrategyThemeOfferMappingEntity.strategy_theme_id
                    == StrategyThemesEntity.strategy_theme_id,
                )
                .filter(StrategyThemesEntity.strategy_id == strategy_id)
                .all()
            )

            offer_ids = [offef[0] for offef in offer_ids]

            today = datetime.now(selected_timezone).strftime("%Y%m%d")
            if keyword:
                keyword = f"%{keyword}%"
                if is_convertible_to_int(keyword):
                    condition.append(OffersEntity.coupon_no.ilike(keyword))
                else:
                    condition.append(OffersEntity.coupon_name.ilike(keyword))  # offer_name

            result = db.query(
                OffersEntity.coupon_no.label("id"),
                OffersEntity.coupon_name.label("name"),
                OffersEntity.coupon_no.label("code"),
            ).filter(
                OffersEntity.coupon_no.in_(offer_ids),
                OffersEntity.benefit_type.isnot(None),
                OffersEntity.available_end_datetime >= today,  # 이벤트 기간 필터
                *condition,
            )

            return [
                IdWithLabel(
                    id=data.id,
                    name=data.name,
                    label=self._create_label(data),
                )
                for data in result
            ]

    def _add_search_offer_condition_by_user(self, user):
        if user.role_id in ("admin", "operator"):
            condition = [OffersEntity.campaign_id.is_(None)]
        else:
            condition = [
                OffersEntity.offer_source != "AICRM",
                OffersEntity.campaign_id.is_(None),
            ]
        return condition

    def get_search_offers(self, keyword: str, user: User) -> list[IdWithLabel]:
        with self.db() as db:
            condition = self._add_search_offer_condition_by_user(user)

            today = datetime.now(selected_timezone).strftime("%Y%m%d")
            if keyword:
                keyword = f"%{keyword}%"
                if is_convertible_to_int(keyword):
                    condition.append(OffersEntity.coupon_no.ilike(keyword))  # coupon_no
                else:
                    condition.append(OffersEntity.coupon_name.ilike(keyword))  # offer_name

            result = (
                db.query(
                    OffersEntity.coupon_no.label("id"),
                    OffersEntity.coupon_name.label("name"),
                    OffersEntity.coupon_no.label("code"),
                )
                .filter(
                    OffersEntity.benefit_type.isnot(None),
                    OffersEntity.available_end_datetime >= today,  # 이벤트 기간 필터
                    *condition,
                )
                .all()
            )

            return [
                IdWithLabel(
                    id=data.id,
                    name=data.name,
                    label=self._create_label(data),
                )
                for data in result
            ]

    def get_offer_detail_for_msggen(self, offer_key: str) -> bool:
        with self.db() as db:
            entity = (
                db.query(
                    OfferDetailsEntity.offer_key,
                    OfferDetailsEntity.apply_offer_amount,
                    OfferDetailsEntity.apply_offer_rate,
                )
                .filter(OfferDetailsEntity.offer_key == offer_key)
                .first()
            )
            # return OfferDetails.from_entity(entity)
            return entity

    def get_offer_detail(self, coupon_no, db: Session) -> Offer:
        entity = db.query(OffersEntity).filter(OffersEntity.coupon_no == coupon_no).first()

        if entity is None:
            raise NotFoundException(detail={"message": "해당 오퍼 정보를 찾지 못했습니다."})

        offer = Offer.model_validate(entity)

        return offer

    def get_offer(self, coupon_no) -> Offer:
        with self.db() as db:
            entity = db.query(OffersEntity).filter(OffersEntity.coupon_no == coupon_no).first()

            if entity is None:
                raise NotFoundException(detail={"message": "오퍼 정보를 찾지 못했습니다."})

            return Offer.model_validate(entity)

    def get_offer_by_id(self, coupon_no) -> Offer:
        with self.db() as db:
            entity = db.query(OffersEntity).filter(OffersEntity.coupon_no == coupon_no).first()

            if entity is None:
                raise NotFoundException(detail={"message": "오퍼 정보를 찾지 못했습니다."})

            return Offer.from_entity(entity)

    def save_new_coupon(self, cafe24_coupon_response: Cafe24CouponResponse, db: Session):
        for coupon in cafe24_coupon_response.coupons:
            offer_entity = OffersEntity(
                coupon_no=coupon.coupon_no,
                coupon_name=coupon.coupon_name,
                coupon_type=coupon.coupon_type,
                coupon_description=coupon.coupon_description,
                coupon_created_at=coupon.created_date,
                benefit_type=coupon.benefit_type,
                benefit_type_name=(
                    Cafe24CouponBenefitType[coupon.benefit_type].value
                    if coupon.benefit_type
                    else None
                ),
                shop_no=str(coupon.shop_no),
                comp_cd=str(coupon.shop_no),
                br_div="",
                is_available=self.is_coupon_avaiable(coupon),
                available_scope=coupon.available_scope,
                available_product_list=coupon.available_product_list,
                available_category_list=coupon.available_category_list,
                issue_max_count_by_user=(
                    int(coupon.issue_max_count_by_user) if coupon.issue_max_count_by_user else None
                ),
                available_begin_datetime=coupon.available_begin_datetime,
                available_end_datetime=coupon.available_end_datetime,
                issue_type=coupon.issue_type,
                issue_sub_type=coupon.issue_sub_type,
                issue_order_path=coupon.issue_order_path,
                issue_order_type=coupon.issue_order_type,
                issue_reserved=coupon.issue_reserved,
                issue_reserved_date=coupon.issue_reserved_date,
                available_period_type=coupon.available_period_type,
                available_site=coupon.available_site,
                available_price_type=coupon.available_price_type,
                is_stopped_issued_coupon=coupon.is_stopped_issued_coupon,
                benefit_text=coupon.benefit_text,
                benefit_price=coupon.benefit_price,
                benefit_percentage=coupon.benefit_percentage,
                benefit_percentage_round_unit=coupon.benefit_percentage_round_unit,
                benefit_percentage_max_price=coupon.benefit_percentage_max_price,
                include_regional_shipping_rate=coupon.include_regional_shipping_rate,
                include_foreign_delivery=coupon.include_foreign_delivery,
                coupon_direct_url=coupon.coupon_direct_url,
                available_date=coupon.available_date,
                available_order_price_type=coupon.available_order_price_type,
                available_min_price=coupon.available_min_price,
                available_amount_type=coupon.available_amount_type,
                send_sms_for_issue=coupon.send_sms_for_issue,
                issue_order_start_date=coupon.issue_order_start_date,
                issue_order_end_date=coupon.issue_order_end_date,
                deleted=coupon.deleted,
                offer_source="cafe24",
                cus_data_batch_yn="N",
                created_by="aivelabs",
                updated_by="aivelabs",
            )

            db.merge(offer_entity)
        db.commit()

    def is_coupon_avaiable(self, coupon):
        if coupon.issue_type == "M" and coupon.issue_sub_type == "M":
            is_available = True
        else:
            is_available = False
        return is_available
