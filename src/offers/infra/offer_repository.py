from contextlib import AbstractContextManager
from datetime import datetime
from typing import Callable

from sqlalchemy import and_, or_
from sqlalchemy.orm import Session

from src.audiences.enums.audience_type import AudienceType
from src.common.timezone_setting import selected_timezone
from src.common.utils.string_utils import is_convertible_to_int
from src.offers.domain.offer import Offer
from src.offers.enums.offer_use_type import OfferUseType
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
        self, based_on, sort_by, start_date, end_date, keyword
    ) -> list[Offer]:
        with self.db() as db:
            base_query = (
                db.query(OffersEntity)
                .filter(
                    and_(
                        OffersEntity.event_end_dt >= start_date,
                        OffersEntity.event_str_dt <= end_date,
                    )
                )
                .order_by(OffersEntity.offer_source, OffersEntity.event_str_dt.desc())
            )

            if keyword:
                base_query = base_query.filter(
                    or_(
                        OffersEntity.offer_name.ilike(f"%{keyword}%"),
                        OffersEntity.event_no.ilike(f"%{keyword}%"),
                        OffersEntity.offer_source.ilike(f"%{keyword}%"),
                        OffersEntity.offer_type_name.ilike(f"%{keyword}%"),
                    )
                )

            offer_entities = base_query.all()
            use_type_dict = {
                v.value: v.description for _, v in OfferUseType.__members__.items()
            }

            offers = []
            for offer in offer_entities:
                temp_offer = Offer.from_entity(offer)
                temp_offer.offer_use_type = use_type_dict.get(
                    temp_offer.offer_use_type, ""
                )
                temp_offer.offer_source = (
                    temp_offer.offer_source if temp_offer.offer_source else ""
                )

                offers.append(temp_offer)

            return offers

    def _create_label(self, data):
        return f"({data.id}) {data.name}"

    def get_search_offers_of_sets(
        self, audience_type_code: str, strategy_id: str, keyword: str, user: User
    ) -> list[IdWithLabel]:
        with self.db() as db:

            condition = self._add_search_offer_condition_by_user(
                audience_type_code, user
            )

            offer_ids = (
                db.query(StrategyThemeOfferMappingEntity.offer_id)
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
                    condition.append(OffersEntity.event_no.ilike(keyword))  # event_no
                else:
                    condition.append(
                        OffersEntity.offer_name.ilike(keyword)
                    )  # offer_name

            result = db.query(
                OffersEntity.offer_id.label("id"),
                OffersEntity.offer_name.label("name"),
                OffersEntity.event_no.label("code"),
            ).filter(
                OffersEntity.offer_id.in_(offer_ids),
                OffersEntity.offer_type_code.isnot(None),
                OffersEntity.event_end_dt >= today,  # 이벤트 기간 필터
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

    def _add_search_offer_condition_by_user(self, audience_type_code, user):
        if user.role_id in ("admin", "operator"):
            if audience_type_code == AudienceType.segment.value:
                condition = [
                    OffersEntity.offer_source == "AICRM",
                    OffersEntity.campaign_id.is_(None),
                ]
            else:
                condition = [OffersEntity.campaign_id.is_(None)]
        else:
            condition = [
                OffersEntity.offer_source != "AICRM",
                OffersEntity.campaign_id.is_(None),
            ]
        return condition

    def get_search_offers(
        self, audience_type_code: str, keyword: str, user: User
    ) -> list[IdWithLabel]:
        with self.db() as db:
            condition = self._add_search_offer_condition_by_user(
                audience_type_code, user
            )

            today = datetime.now(selected_timezone).strftime("%Y%m%d")
            if keyword:
                keyword = f"%{keyword}%"
                if is_convertible_to_int(keyword):
                    condition.append(OffersEntity.event_no.ilike(keyword))  # event_no
                else:
                    condition.append(
                        OffersEntity.offer_name.ilike(keyword)
                    )  # offer_name

            result = db.query(
                OffersEntity.offer_id.label("id"),
                OffersEntity.offer_name.label("name"),
                OffersEntity.event_no.label("code"),
            ).filter(
                OffersEntity.offer_type_code.isnot(None),
                OffersEntity.event_end_dt >= today,  # 이벤트 기간 필터
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
