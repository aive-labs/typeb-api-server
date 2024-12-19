from datetime import datetime
from typing import Optional

from sqlalchemy import func, or_
from sqlalchemy.orm import Session

from src.common.timezone_setting import selected_timezone
from src.common.utils.string_utils import is_convertible_to_int
from src.core.exceptions.exceptions import NotFoundException
from src.offer.domain.cafe24_coupon import Cafe24CouponResponse
from src.offer.domain.offer import Offer
from src.offer.enums.cafe24_coupon_benefit_type import Cafe24CouponBenefitType
from src.offer.infra.entity.offer_details_entity import OfferDetailsEntity
from src.offer.infra.entity.offers_entity import OffersEntity
from src.offer.service.port.base_offer_repository import BaseOfferRepository
from src.search.routes.dto.id_with_label_response import IdWithLabel
from src.strategy.infra.entity.strategy_theme_entity import StrategyThemesEntity
from src.strategy.infra.entity.strategy_theme_offers_entity import (
    StrategyThemeOfferMappingEntity,
)
from src.user.domain.user import User


class OfferRepository(BaseOfferRepository):

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
        # use_type_dict = {v.value: v.description for _, v in OfferUseType.__members__.items()}

        offers = []
        for offer in offer_entities:
            temp_offer = Offer.model_validate(offer)
            temp_offer.available_scope = offer.available_scope
            temp_offer.offer_source = temp_offer.offer_source if temp_offer.offer_source else ""

            offers.append(temp_offer)

        return offers

    def _create_label(self, data):
        return f"({data.id}) {data.name}"

    def get_search_offers_of_sets(
        self,
        strategy_id: str,
        keyword: str,
        user: User,
        db: Session,
        strategy_theme_id: Optional[str] = None,
    ) -> list[IdWithLabel]:

        condition = self._add_search_offer_condition_by_user(user)

        base_query = (
            db.query(StrategyThemeOfferMappingEntity.coupon_no)
            .join(
                StrategyThemesEntity,
                StrategyThemeOfferMappingEntity.strategy_theme_id
                == StrategyThemesEntity.strategy_theme_id,
            )
            .filter(StrategyThemesEntity.strategy_id == strategy_id)
        )

        if strategy_theme_id:
            base_query = base_query.filter(
                StrategyThemesEntity.strategy_theme_id == strategy_theme_id
            )

        offer_ids = base_query.all()
        offer_ids = [offer[0] for offer in offer_ids]

        if keyword:
            keyword = f"%{keyword}%"
            if is_convertible_to_int(keyword):
                condition.append(OffersEntity.coupon_no.ilike(keyword))
            else:
                condition.append(OffersEntity.coupon_name.ilike(keyword))  # offer_name

        today = datetime.now(selected_timezone).strftime("%Y%m%d")

        # 오늘 날짜 기준 사용 가능한 쿠폰 조회
        query = db.query(
            OffersEntity.coupon_no.label("id"),
            OffersEntity.coupon_name.label("name"),
            OffersEntity.coupon_no.label("code"),
        ).filter(
            OffersEntity.benefit_type.isnot(None),
            OffersEntity.coupon_no.in_(offer_ids),
            *condition,
        )

        # 쿠폰 타입에 따른 필터 추가
        query = query.filter(
            or_(
                OffersEntity.available_period_type != "F",
                OffersEntity.available_end_datetime >= today,
            )
        )

        result = query.all()

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

    def get_search_offers(self, keyword: str, user: User, db: Session) -> list[IdWithLabel]:

        condition = self._add_search_offer_condition_by_user(user)

        today = datetime.now(selected_timezone).strftime("%Y%m%d")
        if keyword:
            keyword = f"%{keyword}%"
            if is_convertible_to_int(keyword):
                condition.append(OffersEntity.coupon_no.ilike(keyword))  # coupon_no
            else:
                condition.append(OffersEntity.coupon_name.ilike(keyword))  # offer_name

        # 기본 쿼리 생성
        query = db.query(
            OffersEntity.coupon_no.label("id"),
            OffersEntity.coupon_name.label("name"),
            OffersEntity.coupon_no.label("code"),
        ).filter(
            OffersEntity.benefit_type.isnot(None),
            OffersEntity.is_available.is_(True),
            *condition,
        )

        # 조건에 따른 필터 추가
        query = query.filter(
            or_(
                OffersEntity.available_period_type != "F",
                OffersEntity.available_end_datetime >= today,
            )
        )

        result = query.all()

        return [
            IdWithLabel(
                id=data.id,
                name=data.name,
                label=self._create_label(data),
            )
            for data in result
        ]

    def get_offer_detail_for_msggen(self, offer_key: str, db: Session):
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

    def get_offer(self, coupon_no, db: Session) -> Offer:
        entity = db.query(OffersEntity).filter(OffersEntity.coupon_no == coupon_no).first()

        if entity is None:
            raise NotFoundException(detail={"message": "오퍼 정보를 찾지 못했습니다."})

        return Offer.model_validate(entity)

    def get_offer_by_id(self, coupon_no, db: Session) -> Offer:
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
                    coupon.issue_max_count_by_user if coupon.issue_max_count_by_user else None
                ),
                available_begin_datetime=coupon.available_begin_datetime,
                available_end_datetime=coupon.available_end_datetime,
                available_day_from_issued=coupon.available_day_from_issued,
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

    def get_offer_count(self, db) -> int:
        return db.query(func.count(OffersEntity.coupon_no)).scalar()
