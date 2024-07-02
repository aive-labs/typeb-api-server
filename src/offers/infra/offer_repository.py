from contextlib import AbstractContextManager
from datetime import datetime
from typing import Callable

from sqlalchemy import and_, or_
from sqlalchemy.orm import Session

from src.common.infra.entity.channel_master_entity import ChannelMasterEntity
from src.common.timezone_setting import selected_timezone
from src.common.utils.string_utils import is_convertible_to_int
from src.contents.infra.entity.style_master_entity import StyleMasterEntity
from src.core.exceptions.exceptions import NotFoundException
from src.offers.domain.offer import Offer
from src.offers.domain.offer_condition_variable import OfferConditionVar
from src.offers.domain.offer_option import OfferOption
from src.offers.enums.offer_type import OfferType
from src.offers.enums.offer_use_type import OfferUseType
from src.offers.infra.entity.offer_duplicate_entity import OfferDuplicateEntity
from src.offers.infra.entity.offers_entity import OffersEntity
from src.offers.routes.dto.response.offer_detail_response import OfferDetailResponse
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
        self, strategy_id: str, keyword: str, user: User
    ) -> list[IdWithLabel]:
        with self.db() as db:

            condition = self._add_search_offer_condition_by_user(user)

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

    def get_offer_detail(self, offer_key) -> OfferDetailResponse:
        with self.db() as db:
            offer_data = (
                db.query(OffersEntity)
                .filter(OffersEntity.offer_key == offer_key)
                .first()
            )
            style_data = db.query(StyleMasterEntity).all()
            channel_data = db.query(ChannelMasterEntity).all()

            dupl_apply_event = (
                db.query(OffersEntity.event_no, OffersEntity.offer_name)
                .filter(
                    (OffersEntity.offer_key != offer_key)
                    & (OffersEntity.offer_use_type != "2")
                )
                .all()
            )

            offer_type_dict = {
                v.code: v.description for _, v in OfferType.__members__.items()
            }

            if offer_data is None:
                raise NotFoundException(
                    detail={"message": "해당 오퍼 정보를 찾지 못했습니다."}
                )

            offer_data = Offer.from_entity(offer_data)

            offer_cond = OfferConditionVar()

            sty_cond_options = offer_cond.cond_option(
                offer_cond.sty_condition_dict, style_data, OfferOption
            )
            chn_cond_options = offer_cond.cond_option(
                offer_cond.chn_condition_dict, channel_data, OfferOption
            )

            offer_options = [
                OfferOption(id=str(k), name=v)  ## option string으로 변경
                for k, v in offer_type_dict.items()
            ]
            dupl_apply_event = [
                OfferOption(id=k, name=f"({k}) {v}") for k, v in dupl_apply_event
            ]

            return OfferDetailResponse(
                offer_obj=offer_data,
                offer_type_options=offer_options,
                style_options=sty_cond_options,
                channel_options=chn_cond_options,
                dupl_apply_event_options=dupl_apply_event,
            )

    def is_existing_duplicated_date_event(self, offer_update):
        with self.db() as db:
            duplicated_date_event = (
                db.query(OffersEntity)
                .filter(
                    and_(
                        OffersEntity.offer_id != offer_update.offer_id,
                        OffersEntity.event_no == offer_update.event_no,
                        OffersEntity.event_str_dt <= offer_update.event_end_dt,
                        OffersEntity.event_end_dt >= offer_update.event_str_dt,
                    )
                )
                .first()
            )

            if duplicated_date_event is None:
                return False

            return True

    def get_offer(self, offer_key) -> Offer:
        with self.db() as db:
            entity = (
                db.query(OffersEntity)
                .filter(OffersEntity.offer_key == offer_key)
                .first()
            )

            if entity is None:
                raise NotFoundException("오퍼 정보를 찾지 못했습니다.")

            return Offer.from_entity(entity)

    def save_duplicate_offer(
        self, offer_id, event_no, offer_update, now_kst_datetime, user
    ):
        with self.db() as db:
            db.query(OfferDuplicateEntity).filter(
                (OfferDuplicateEntity.event_no == event_no)
                & (OfferDuplicateEntity.offer_id == offer_id)
            ).delete()

            dupl_apply_obj = [
                OfferDuplicateEntity(
                    offer_id=offer_id,
                    event_no=event_no,
                    incs_event_no=dupl_apply_event_no,
                    created_by=user.username,
                    updated_by=user.username,
                    updated_at=now_kst_datetime,
                )
                for dupl_apply_event_no in offer_update.dupl_apply_event
            ]
            db.bulk_save_objects(dupl_apply_obj)

            db.commit()
