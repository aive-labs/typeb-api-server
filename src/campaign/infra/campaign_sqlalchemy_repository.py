from collections.abc import Callable
from contextlib import AbstractContextManager

from sqlalchemy import and_, func, not_, or_
from sqlalchemy.orm import Session

from src.campaign.domain.campaign import Campaign
from src.campaign.enums.campagin_status import CampaignStatus
from src.campaign.enums.send_type import SendType
from src.campaign.infra.entity.campaign_entity import CampaignEntity
from src.common.sqlalchemy.object_access_condition import object_access_condition
from src.users.domain.user import User


class CampaignSqlAlchemy:

    def __init__(self, db: Callable[..., AbstractContextManager[Session]]):
        """_summary_

        Args:
            db (Callable[..., AbstractContextManager[Session]]):
            - Callable 호출 가능한 객체
            - AbstractContextManager[Session]: 세션 객체를 반환하는 컨텍스트 관리자
            - Session: SQLAlchemy의 세션 객체
        """
        self.db = db

    def get_campaign_by_name(self, name: str):
        with self.db() as db:
            return (
                db.query(CampaignEntity)
                .filter(CampaignEntity.campaign_name == name)
                .first()
            )

    def get_all_campaigns(
        self, start_date: str, end_date: str, user: User
    ) -> list[Campaign]:
        with self.db() as db:

            conditions = object_access_condition(db=db, user=user, model=CampaignEntity)

            campaign_entities = (
                db.query(CampaignEntity)
                .filter(
                    or_(
                        and_(
                            CampaignEntity.send_type_code == SendType.onetime.value,
                            not_(
                                or_(
                                    CampaignEntity.start_date > end_date,
                                    CampaignEntity.end_date < start_date,
                                )
                            ),
                        ),
                        and_(  # 주기성(진행대기, 운영중 ..~) -> 캠페인기간이 날짜필터 기간에 겹치는 오브젝트만 리스트업
                            CampaignEntity.send_type_code == SendType.recurring.value,
                            ~CampaignEntity.campaign_status_code.in_(
                                [
                                    CampaignStatus.tempsave.value,
                                    CampaignStatus.review.value,
                                ]
                            ),
                            not_(
                                or_(
                                    CampaignEntity.start_date > end_date,
                                    CampaignEntity.end_date < start_date,
                                )
                            ),
                        ),
                        and_(  # 주기성(임시저장,리뷰단계) -> 생성일이후 오브젝트만 리스트업
                            CampaignEntity.send_type_code == SendType.recurring.value,
                            CampaignEntity.campaign_status_code.in_(
                                [
                                    CampaignStatus.tempsave.value,
                                    CampaignStatus.review.value,
                                ]
                            ),
                            func.date(CampaignEntity.created_at) >= start_date,
                        ),
                    ),
                    *conditions
                )
                .all()
            )

            campaigns = [
                Campaign.model_validate(entity) for entity in campaign_entities
            ]

            return campaigns
