from collections.abc import Callable
from contextlib import AbstractContextManager

from sqlalchemy import func, or_
from sqlalchemy.orm import Session

from src.audiences.infra.entity.theme_audience_entity import ThemeAudienceEntity
from src.common.enums.role import RoleEnum
from src.core.exceptions import NotFoundError
from src.strategy.domain.campaign_theme import CampaignTheme
from src.strategy.domain.strategy import Strategy
from src.strategy.enums.strategy_status import StrategyStatus
from src.strategy.infra.entity.campaign_theme_entity import CampaignThemeEntity
from src.strategy.infra.entity.strategy_entity import StrategyEntity
from src.strategy.infra.entity.theme_offers_entity import ThemeOfferEntity
from src.users.domain.user import User
from src.users.infra.entity.user_entity import UserEntity
from src.utils.date_utils import localtime_converter


class StrategySqlAlchemy:

    def __init__(self, db: Callable[..., AbstractContextManager[Session]]):
        """_summary_

        Args:
            db (Callable[..., AbstractContextManager[Session]]):
            - Callable 호출 가능한 객체
            - AbstractContextManager[Session]: 세션 객체를 반환하는 컨텍스트 관리자
            - Session: SQLAlchemy의 세션 객체

        """
        self.db = db

    def get_all_strategies(
        self, start_date, end_date, user: User
    ) -> list[StrategyEntity]:
        with self.db() as db:

            user_entity = (
                db.query(UserEntity).filter(UserEntity.id == user.user_id).first()
            )

            conditions = self._object_access_condition(db, user_entity, StrategyEntity)

            return (
                db.query(StrategyEntity)
                .filter(
                    or_(
                        func.date(StrategyEntity.updated_at) >= start_date,
                        func.date(StrategyEntity.updated_at) <= end_date,
                    ),
                    StrategyEntity.strategy_status_code
                    != StrategyStatus.notdisplay.value,
                    *conditions
                )
                .all()
            )

    def get_strategy_detail(self, strategy_id: str) -> StrategyEntity:
        with self.db() as db:
            result = (
                db.query(StrategyEntity)
                .filter(StrategyEntity.strategy_id == strategy_id)
                .first()
            )

            if result is None:
                raise NotFoundError("전략을 찾지 못했습니다.")

            return result

    def create_strategy(
        self, strategy: Strategy, campaign_themes: list[CampaignTheme], user: User
    ):
        with self.db() as db:
            strategy_entity = StrategyEntity(
                strategy_name=strategy.strategy_name,
                strategy_tags=strategy.strategy_tags,
                strategy_metric_code=strategy.strategy_metric_code,
                strategy_metric_name=strategy.strategy_metric_name,
                strategy_status_code=strategy.strategy_status_code,
                strategy_status_name=strategy.strategy_status_name,
                audience_type_code=strategy.audience_type_code,
                audience_type_name=strategy.audience_type_name,
                target_group_code=strategy.target_group_code,
                target_group_name=strategy.target_group_name,
                created_by=user.username,
                created_at=localtime_converter(),
                updated_by=user.username,
                updated_at=localtime_converter(),
                owned_by_dept=user.department_id,
            )

            for theme in campaign_themes:
                campaign_theme_entity = CampaignThemeEntity(
                    campaign_theme_name=theme.campaign_theme_name,
                    recsys_model_id=theme.recsys_model_id,
                    contents_tags=theme.contents_tags,
                )

                theme_audience_entities = [
                    ThemeAudienceEntity(audience_id=audience.audience_id)
                    for audience in theme.theme_audience
                ]

                for theme_audience_entity in theme_audience_entities:
                    campaign_theme_entity.theme_audience_mapping.append(
                        theme_audience_entity
                    )

                theme_offer_entities = [
                    ThemeOfferEntity(offer_id=offer.offer_id)
                    for offer in theme.theme_offer
                ]

                for theme_offer_entity in theme_offer_entities:
                    campaign_theme_entity.theme_offer_mapping.append(theme_offer_entity)

                strategy_entity.campaign_themes.append(campaign_theme_entity)

            db.add(strategy_entity)

    def _object_access_condition(
        self, db: Session, user: UserEntity, model: StrategyEntity
    ):
        """Checks if the user has the required permissions for Object access.
        Return conditions based on object access permissions

        Args:
            dep: The object obtained from the `verify_user` dependency.
            model: Object Model
        """
        admin_access = (
            True
            if user.role_id in [RoleEnum.ADMIN.value, RoleEnum.OPERATOR.value]
            else False
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
                    db.query(User.department_id)
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

    def is_strategy_name_exists(self, name: str) -> int:
        with self.db() as db:
            return (
                db.query(StrategyEntity)
                .filter(StrategyEntity.strategy_name == name)
                .count()
            )

    def find_by_strategy_id(self, strategy_id: str) -> Strategy:
        with self.db() as db:
            entity = (
                db.query(StrategyEntity)
                .filter(StrategyEntity.strategy_id == strategy_id)
                .first()
            )

            return Strategy.from_entity(entity)
