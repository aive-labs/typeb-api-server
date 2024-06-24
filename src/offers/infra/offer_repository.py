from contextlib import AbstractContextManager
from datetime import datetime
from typing import Callable

from sqlalchemy.orm import Session

from src.audiences.enums.audience_type import AudienceType
from src.common.timezone_setting import selected_timezone
from src.common.utils.string_utils import is_convertible_to_int
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
