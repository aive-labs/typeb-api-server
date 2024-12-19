from typing import Type

from sqlalchemy import func, or_, update
from sqlalchemy.orm import Session

from src.audience.infra.entity.strategy_theme_audience_entity import (
    StrategyThemeAudienceMappingEntity,
)
from src.common.model.role import RoleEnum
from src.common.utils.date_utils import localtime_converter
from src.main.exceptions.exceptions import NotFoundException
from src.search.model.id_with_item_response import IdWithItem
from src.search.model.strategy_search_response import StrategySearchResponse
from src.strategy.domain.strategy import Strategy
from src.strategy.domain.strategy_theme import StrategyTheme
from src.strategy.infra.entity.strategy_entity import StrategyEntity
from src.strategy.infra.entity.strategy_theme_entity import StrategyThemesEntity
from src.strategy.infra.entity.strategy_theme_offers_entity import (
    StrategyThemeOfferMappingEntity,
)
from src.strategy.model.strategy_status import StrategyStatus
from src.user.domain.user import User
from src.user.infra.entity.user_entity import UserEntity


class StrategySqlAlchemy:
    def get_all_strategies(self, start_date, end_date, user: User, db: Session) -> list[Strategy]:

        user_entity = db.query(UserEntity).filter(UserEntity.user_id == user.user_id).first()

        conditions = self._object_access_condition(db, user_entity, StrategyEntity)

        entities = (
            db.query(StrategyEntity)
            .filter(
                or_(
                    func.date(StrategyEntity.updated_at) >= start_date,
                    func.date(StrategyEntity.updated_at) <= end_date,
                ),
                ~StrategyEntity.is_deleted,
                StrategyEntity.strategy_status_code != StrategyStatus.notdisplay.value,
                *conditions,
            )
            .all()
        )
        return [Strategy.from_entity(entity) for entity in entities]

    def get_strategy_detail(self, strategy_id: str, db: Session) -> Strategy:

        entity: StrategyEntity = (
            db.query(StrategyEntity)
            .filter(
                ~StrategyEntity.is_deleted,
                StrategyEntity.strategy_id == strategy_id,
            )
            .first()
        )

        if entity is None:
            raise NotFoundException(detail={"message": "전략을 찾지 못했습니다."})

        return Strategy.from_entity(entity)

    def create_strategy(
        self, strategy: Strategy, strategy_themes: list[StrategyTheme], user: User, db: Session
    ) -> StrategyEntity:

        strategy_entity = StrategyEntity(
            strategy_name=strategy.strategy_name,
            strategy_tags=strategy.strategy_tags,
            strategy_status_code=strategy.strategy_status_code,
            strategy_status_name=strategy.strategy_status_name,
            target_strategy=strategy.target_strategy,
            created_by=user.username,
            created_at=localtime_converter(),
            updated_by=user.username,
            updated_at=localtime_converter(),
            owned_by_dept=user.department_id,
        )

        for theme in strategy_themes:
            strategy_theme_entity = StrategyThemesEntity(
                strategy_theme_name=theme.strategy_theme_name,
                recsys_model_id=theme.recsys_model_id,
                contents_tags=theme.contents_tags,
            )

            theme_audience_entities = [
                StrategyThemeAudienceMappingEntity(audience_id=audience.audience_id)
                for audience in theme.strategy_theme_audience_mapping
            ]

            for theme_audience_entity in theme_audience_entities:
                strategy_theme_entity.strategy_theme_audience_mapping.append(theme_audience_entity)

            theme_offer_entities = [
                StrategyThemeOfferMappingEntity(coupon_no=coupon.coupon_no)
                for coupon in theme.strategy_theme_offer_mapping
            ]

            for theme_offer_entity in theme_offer_entities:
                strategy_theme_entity.strategy_theme_offer_mapping.append(theme_offer_entity)

            strategy_entity.strategy_themes.append(strategy_theme_entity)

        db.add(strategy_entity)
        db.commit()

        return strategy_entity

    def _object_access_condition(self, db: Session, user: UserEntity, model: Type[StrategyEntity]):
        """Checks if the user has the required permissions for Object access.
        Return conditions based on object access permissions

        Args:
            dep: The object obtained from the `verify_user` dependency.
            model: Object Model
        """
        admin_access = (
            True if user.role_id in [RoleEnum.ADMIN.value, RoleEnum.OPERATOR.value] else False
        )

        if admin_access:
            res_cond = []
        else:
            # 생성부서(매장) 또는 생성매장의 branch_manager
            conditions = [model.owned_by_dept == user.department_id]

            # 일반 이용자
            if user.sys_id == "HO":
                if user.parent_dept_cd:
                    ##본부 하위 팀 부서 리소스
                    parent_teams_query = db.query(UserEntity).filter(
                        UserEntity.parent_dept_cd == user.parent_dept_cd
                    )
                    department_ids = list({i.department_id for i in parent_teams_query})
                    team_conditions = [model.owned_by_dept.in_(department_ids)]  # type: ignore
                    conditions.extend(team_conditions)
                    erp_ids = [i.erp_id for i in parent_teams_query]
                else:
                    dept_query = db.query(UserEntity).filter(
                        UserEntity.department_id == user.department_id
                    )
                    erp_ids = [i.erp_id for i in dept_query]

                # 해당 본사 팀이 관리하는 매장 리소스
                shops_query = (
                    db.query(UserEntity.department_id)
                    .filter(
                        UserEntity.branch_manager.in_(erp_ids),
                        UserEntity.branch_manager.isnot(None),
                    )
                    .filter()
                    .distinct()
                )
                shop_codes = [i[0] for i in shops_query]
                branch_conditions = [model.owned_by_dept.in_(shop_codes)]  # type: ignore
                conditions.extend(branch_conditions)

                res_cond = [or_(*conditions)]

            # 매장 이용자
            else:
                res_cond = conditions

        return res_cond

    def is_strategy_name_exists(self, name: str, db: Session) -> int:
        return (
            db.query(StrategyEntity)
            .filter(~StrategyEntity.is_deleted, StrategyEntity.strategy_name == name)
            .count()
        )

    def find_by_strategy_id(self, strategy_id: str) -> Strategy:
        with self.db() as db:
            entity = (
                db.query(StrategyEntity)
                .filter(
                    ~StrategyEntity.is_deleted,
                    StrategyEntity.strategy_id == strategy_id,
                )
                .first()
            )

            return Strategy.from_entity(entity)

    def delete(self, strategy_id, db: Session):

        update_statement = (
            update(StrategyEntity)
            .where(StrategyEntity.strategy_id == strategy_id)
            .values(is_deleted=True)
        )

        db.execute(update_statement)

        strategy_theme = (
            db.query(StrategyThemesEntity)
            .filter(StrategyThemesEntity.strategy_id == strategy_id)
            .first()
        )

        db.delete(strategy_theme)

    def update_expired_strategy(self, strategy_id, db: Session):

        update_statement = (
            update(StrategyEntity)
            .where(StrategyEntity.strategy_id == strategy_id)
            .values(
                strategy_status_code=StrategyStatus.notdisplay.value,
                strategy_status_name=StrategyStatus.notdisplay.description,
            )
        )

        db.execute(update_statement)

    def update(
        self,
        strategy: Strategy,
        strategy_themes: list[StrategyTheme],
        user: User,
        db: Session,
    ):
        strategy_entity = StrategyEntity(
            strategy_id=strategy.strategy_id,
            strategy_name=strategy.strategy_name,
            strategy_tags=strategy.strategy_tags,
            strategy_status_code=strategy.strategy_status_code,
            strategy_status_name=strategy.strategy_status_name,
            target_strategy=strategy.target_strategy,
            updated_by=user.username,
            updated_at=localtime_converter(),
            owned_by_dept=user.department_id,
        )

        for theme in strategy_themes:
            strategy_theme_entity = StrategyThemesEntity(
                strategy_theme_id=theme.strategy_theme_id,
                strategy_theme_name=theme.strategy_theme_name,
                strategy_id=strategy.strategy_id,
                recsys_model_id=theme.recsys_model_id,
                contents_tags=theme.contents_tags,
                updated_by=theme.updated_by,
            )

            theme_audience_entities = [
                StrategyThemeAudienceMappingEntity(
                    audience_id=audience.audience_id,
                    strategy_theme_id=theme.strategy_theme_id,
                    updated_by=theme.updated_by,
                    updated_at=theme.updated_at,
                )
                for audience in theme.strategy_theme_audience_mapping
            ]

            for theme_audience_entity in theme_audience_entities:
                strategy_theme_entity.strategy_theme_audience_mapping.append(theme_audience_entity)

            theme_offer_entities = [
                StrategyThemeOfferMappingEntity(
                    coupon_no=coupon.coupon_no,
                    strategy_theme_id=theme.strategy_theme_id,
                    updated_by=theme.updated_by,
                    updated_at=theme.updated_at,
                )
                for coupon in theme.strategy_theme_offer_mapping
            ]

            for theme_offer_entity in theme_offer_entities:
                strategy_theme_entity.strategy_theme_offer_mapping.append(theme_offer_entity)

            strategy_entity.strategy_themes.append(strategy_theme_entity)

        db.merge(strategy_entity)

    def is_strategy_name_exists_for_update(self, strategy_id, name, db):
        return (
            db.query(StrategyEntity)
            .filter(
                ~StrategyEntity.is_deleted,
                StrategyEntity.strategy_name == name,
                StrategyEntity.strategy_id != strategy_id,
            )
            .count()
        )

    def search_keyword(
        self, campaign_type_code, search_keyword, db
    ) -> list[StrategySearchResponse]:

        if search_keyword:
            keyword = f"%{search_keyword}%"

            entities = (
                db.query(
                    StrategyEntity.strategy_id,
                    StrategyEntity.strategy_name,
                    StrategyEntity.strategy_tags,
                    StrategyEntity.target_strategy,
                )
                .filter(StrategyEntity.strategy_name.ilike(keyword))
                .all()
            )
        else:
            entities = (
                db.query(
                    StrategyEntity.strategy_id,
                    StrategyEntity.strategy_name,
                    StrategyEntity.strategy_tags,
                    StrategyEntity.target_strategy,
                )
                .filter(~StrategyEntity.is_deleted)
                .all()
            )

        return [
            StrategySearchResponse(
                strategy_id=entity.strategy_id,
                strategy_name=entity.strategy_name,
                strategy_tags=entity.strategy_tags,
                target_strategy=entity.target_strategy,
            )
            for entity in entities
        ]

    def search_strategy_themes_by_strategy_id(self, strategy_id, db) -> list[IdWithItem]:
        entities = (
            db.query(StrategyThemesEntity)
            .filter(StrategyThemesEntity.strategy_id == strategy_id)
            .all()
        )
        return [
            IdWithItem(id=entity.strategy_theme_id, name=entity.strategy_theme_name)
            for entity in entities
        ]

    def get_tags(self, strategy_theme_id, db: Session):
        entity = (
            db.query(StrategyThemesEntity.contents_tags, StrategyThemesEntity.recsys_model_id)
            .filter(StrategyThemesEntity.strategy_theme_id == strategy_theme_id)
            .first()
        )

        if not entity:
            raise NotFoundException(detail={"message": "전략테마를 찾을 수 없습니다."})

        return entity.contents_tags, entity.recsys_model_id

    def get_recsys_id_by_strategy_theme_by_id(self, strategy_theme_id, db: Session) -> int | None:
        entity = (
            db.query(StrategyThemesEntity)
            .filter(StrategyThemesEntity.strategy_theme_id == strategy_theme_id)
            .first()
        )

        if entity is None:
            return None

        return entity.recsys_model_id
