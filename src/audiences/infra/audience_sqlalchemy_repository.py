from collections.abc import Callable
from contextlib import AbstractContextManager

from sqlalchemy import and_, func, or_
from sqlalchemy.orm import Session

from src.audiences.enums.audience_status import AudienceStatus
from src.audiences.infra.dto.audience_info import AudienceInfo
from src.audiences.infra.dto.linked_campaign import LinkedCampaign
from src.audiences.infra.entity.audience_count_by_month_entity import (
    AudienceCountByMonthEntity,
)
from src.audiences.infra.entity.audience_customer_mapping_entity import (
    AudienceCustomerMapping,
)
from src.audiences.infra.entity.audience_entity import AudienceEntity
from src.audiences.infra.entity.audience_queries_entity import AudienceQueries
from src.audiences.infra.entity.audience_stats_entity import AudienceStatsEntity
from src.audiences.infra.entity.audience_upload_condition_entity import (
    AudienceUploadConditions,
)
from src.audiences.infra.entity.primary_rep_product_entity import (
    PrimaryRepProductEntity,
)
from src.audiences.infra.entity.theme_audience import ThemeAudience
from src.campaign.infra.entity.campaigns_entity import Campaigns
from src.common.enums.role import RoleEnum
from src.core.exceptions import NotFoundError
from src.strategy.infra.entity.strategy_themes_entity import StrategyThemes
from src.users.domain.user import User
from src.users.infra.entity.user_entity import UserEntity


class AudienceSqlAlchemy:

    def __init__(self, db: Callable[..., AbstractContextManager[Session]]):
        """_summary_

        Args:
            db (Callable[..., AbstractContextManager[Session]]):
            - Callable 호출 가능한 객체
            - AbstractContextManager[Session]: 세션 객체를 반환하는 컨텍스트 관리자
            - Session: SQLAlchemy의 세션 객체

        """
        self.db = db

    def get_audiences(
        self, user: User, is_exclude: bool | None = None
    ) -> list[AudienceInfo]:
        with self.db() as db:

            user_entity = (
                db.query(UserEntity).filter(UserEntity.id == user.user_id).first()
            )
            if user_entity is None:
                raise NotFoundError("사용자를 찾지 못했습니다.")

            if is_exclude:
                conditions = [AudienceEntity.is_exclude == is_exclude]
                func.concat(
                    "(", AudienceEntity.audience_id, ") ", AudienceEntity.audience_name
                ).label("audience_name")

            else:
                conditions = self._object_access_condition(
                    db=db, user=user_entity, model=AudienceEntity
                )

            subq = (
                db.query(
                    AudienceCountByMonthEntity.audience_id,
                    func.max(AudienceCountByMonthEntity.stnd_month).label("maxdate"),
                )
                .group_by(AudienceCountByMonthEntity.audience_id)
                .subquery()
            )

            subq_maxdate = (
                db.query(AudienceCountByMonthEntity)
                .join(
                    subq,
                    and_(
                        AudienceCountByMonthEntity.audience_id == subq.c.audience_id,
                        AudienceCountByMonthEntity.stnd_month == subq.c.maxdate,
                    ),
                )
                .subquery()
            )

            audience_filtered = (
                db.query(
                    AudienceEntity.audience_id,
                    AudienceEntity.audience_name,
                    AudienceEntity.audience_type_code,
                    AudienceEntity.audience_type_name,
                    AudienceEntity.audience_status_code,
                    AudienceEntity.audience_status_name,
                    AudienceEntity.is_exclude,
                    AudienceEntity.user_exc_deletable,
                    AudienceEntity.update_cycle,
                    AudienceEntity.description,
                    AudienceEntity.created_at,
                    AudienceEntity.updated_at,
                    subq_maxdate.c.audience_count,
                    AudienceStatsEntity.audience_unit_price,
                    PrimaryRepProductEntity.main_product_id,
                    PrimaryRepProductEntity.main_product_name,
                )
                .join(
                    subq_maxdate,
                    AudienceEntity.audience_id == subq_maxdate.c.audience_id,
                )
                .join(
                    AudienceStatsEntity,
                    AudienceEntity.audience_id == AudienceStatsEntity.audience_id,
                )
                .outerjoin(
                    PrimaryRepProductEntity,
                    AudienceEntity.audience_id == PrimaryRepProductEntity.audience_id,
                )
                .filter(
                    AudienceEntity.audience_status_code
                    != AudienceStatus.notdisplay.value,
                    *conditions
                )
            )

            result = audience_filtered.all()

            # 결과를 Pydantic 모델로 변환
            audiences = AudienceInfo.from_query(result)
            return audiences

    def get_audience(self, audience_id: str) -> AudienceEntity | None:
        with self.db() as db:
            return (
                db.query(AudienceEntity)
                .filter(AudienceEntity.audience_id == audience_id)
                .first()
            )

    def get_linked_campaign(self, audience_id: str) -> list[LinkedCampaign]:
        with self.db() as db:
            results = (
                db.query(ThemeAudience.audience_id, Campaigns.campaign_status_code)
                .join(
                    StrategyThemes,
                    ThemeAudience.campaign_theme_id == StrategyThemes.campaign_theme_id,
                )
                .join(Campaigns, StrategyThemes.strategy_id == Campaigns.strategy_id)
                .filter(ThemeAudience.audience_id == audience_id)
                .all()
            )

            linked_campaigns = [
                LinkedCampaign(audience_id=row[0], campaign_status_code=row[1])
                for row in results
            ]
            return linked_campaigns

    def update_expired_audience_status(self, audience_id: str):
        with self.db() as db:
            db.query(AudienceEntity).filter(
                AudienceEntity.audience_id == audience_id
            ).update(
                {
                    "audience_status_code": "notdisplay",
                    "audience_status_name": "미표시",
                },
                synchronize_session=False,
            )

            db.commit()

    def delete_audience(self, audience_id: str):
        with self.db() as db:
            # 타겟 오디언스
            db.query(AudienceEntity).filter(
                AudienceEntity.audience_id == audience_id
            ).delete()

            # 상세정보
            db.query(AudienceStatsEntity).filter(
                AudienceStatsEntity.audience_id == audience_id
            ).delete()

            # 오디언스 생성 쿼리
            db.query(AudienceQueries).filter(
                AudienceQueries.audience_id == audience_id
            ).delete()

            # 오디언스 업로드 정보
            db.query(AudienceUploadConditions).filter(
                AudienceUploadConditions.audience_id == audience_id
            ).delete()

            # 타겟 오디언스 수
            db.query(AudienceCountByMonthEntity).filter(
                AudienceCountByMonthEntity.audience_id == audience_id
            ).delete()

            # 타겟 오디언스 주 구매 대표상품
            db.query(PrimaryRepProductEntity).filter(
                PrimaryRepProductEntity.audience_id == audience_id
            ).delete()

            # 타겟오디언스 고객 리스트
            db.query(AudienceCustomerMapping).filter(
                AudienceCustomerMapping.audience_id == audience_id
            ).delete()

            db.commit()

    def _object_access_condition(
        self, db: Session, user: UserEntity, model: AudienceEntity
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
