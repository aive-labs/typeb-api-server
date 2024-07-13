from collections.abc import Callable
from contextlib import AbstractContextManager

from sqlalchemy import Integer, and_, desc, distinct, func, not_, or_
from sqlalchemy.orm import Session, joinedload

from src.audiences.infra.entity.variable_table_list import CustomerInfoStatusEntity
from src.campaign.domain.campaign import Campaign
from src.campaign.domain.campaign_messages import CampaignMessages, SetGroupMessages
from src.campaign.domain.campaign_timeline import CampaignTimeline
from src.campaign.domain.send_reservation import SendReservation
from src.campaign.enums.campagin_status import CampaignStatus
from src.campaign.enums.send_type import SendType
from src.campaign.infra.entity.campaign_entity import CampaignEntity
from src.campaign.infra.entity.campaign_remind_entity import CampaignRemindEntity
from src.campaign.infra.entity.campaign_set_recipients_entity import (
    CampaignSetRecipientsEntity,
)
from src.campaign.infra.entity.campaign_sets_entity import CampaignSetsEntity
from src.campaign.infra.entity.campaign_timeline_entity import CampaignTimelineEntity
from src.campaign.infra.entity.send_reservation_entity import SendReservationEntity
from src.campaign.infra.entity.set_group_messages_entity import SetGroupMessagesEntity
from src.common.sqlalchemy.object_access_condition import object_access_condition
from src.common.utils.string_utils import is_convertible_to_int
from src.contents.infra.entity.style_master_entity import StyleMasterEntity
from src.search.routes.dto.id_with_item_response import IdWithItem
from src.users.domain.user import User
from src.users.infra.entity.user_entity import UserEntity


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
                    *conditions,
                )
                .all()
            )

            campaigns = [
                Campaign.model_validate(entity) for entity in campaign_entities
            ]

            return campaigns

    def is_existing_campaign_by_offer_event_no(self, offer_event_no):
        with self.db() as db:
            used_event_no = (
                db.query(CampaignSetsEntity)
                .join(
                    CampaignEntity,
                    CampaignSetsEntity.campaign_id == CampaignEntity.campaign_id,
                )
                .filter(
                    CampaignEntity.campaign_status_code.notin_(["o2", "s3"]),
                    CampaignSetsEntity.event_no == offer_event_no,
                )
                .first()
            )

            if used_event_no is None:
                return False

            return True

    def get_campaign_by_strategy_id(
        self, strategy_id: str, db: Session
    ) -> list[Campaign]:
        entities = (
            db.query(CampaignEntity)
            .filter(CampaignEntity.strategy_id == strategy_id)
            .distinct()
            .all()
        )

        return [Campaign.model_validate(entity) for entity in entities]

    def get_timeline(self, campaign_id, db) -> list[CampaignTimeline]:
        timelines = (
            db.query(
                CampaignTimelineEntity.timeline_no,
                CampaignTimelineEntity.timeline_type,
                CampaignTimelineEntity.description,
                CampaignTimelineEntity.status_no,
                CampaignTimelineEntity.created_at,
                CampaignTimelineEntity.created_by,
                CampaignTimelineEntity.created_by_name,
                UserEntity.email,
                UserEntity.photo_uri,
                UserEntity.department_id,
                UserEntity.department_name,
                UserEntity.test_callback_number,
            )
            .outerjoin(
                UserEntity,
                func.cast(CampaignTimelineEntity.created_by, Integer)
                == UserEntity.user_id,
            )
            .filter(
                CampaignTimelineEntity.campaign_id == campaign_id,
            )
            .order_by(desc(CampaignTimelineEntity.timeline_no))
            .all()
        )

        return [CampaignTimeline.model_validate(timeline) for timeline in timelines]

    def search_campaign(
        self, keyword, current_date, two_weeks_ago, db
    ) -> list[IdWithItem]:
        conditions = []

        if keyword:
            modified_string = keyword.replace("cam-", "")
            keyword = f"%{keyword}%"

            if is_convertible_to_int(modified_string):
                conditions.append(
                    CampaignEntity.campaign_id.ilike(keyword)
                )  # audience_id
            else:
                conditions.append(
                    CampaignEntity.campaign_name.ilike(keyword)
                )  # audience_name

        entities = (
            db.query(
                CampaignEntity.campaign_id.label("id"),
                CampaignEntity.campaign_name.label("name"),
            )
            .filter(
                CampaignEntity.start_date <= current_date,
                CampaignEntity.end_date >= two_weeks_ago,
                CampaignEntity.campaign_status_code.notin_(["r1"]),
                *conditions,
            )
            .all()
        )

        return [IdWithItem(id=entity.id, name=entity.name) for entity in entities]

    def get_send_complete_campaign(
        self, campaign_id, req_set_group_seqs, db
    ) -> SendReservation:
        return (
            db.query(SendReservationEntity)
            .filter(
                SendReservationEntity.campaign_id == campaign_id,
                SendReservationEntity.test_send_yn == "n",
                SendReservationEntity.set_group_msg_seq.in_(req_set_group_seqs),
                SendReservationEntity.send_resv_state.not_in(
                    ["21", "01", "00"]
                ),  # 발송한 메세지 필터
            )
            .first()
        )

    def get_group_item_nm_stats(self, campaign_id, set_sort_num):
        with self.db() as db:
            subquery = db.query(
                distinct(StyleMasterEntity.rep_nm).label("rep_nm"),
                StyleMasterEntity.item_nm,
            ).subquery()

            return (
                db.query(
                    CampaignSetRecipientsEntity.group_sort_num,
                    subquery.c.item_nm,
                    func.count(CampaignSetRecipientsEntity.cus_cd).label("cus_count"),
                )
                .join(subquery, CampaignSetRecipientsEntity.rep_nm == subquery.c.rep_nm)
                .filter(
                    CampaignSetRecipientsEntity.campaign_id == campaign_id,
                    CampaignSetRecipientsEntity.set_sort_num == set_sort_num,
                )
                .group_by(
                    CampaignSetRecipientsEntity.group_sort_num, subquery.c.item_nm
                )
                .all()
            )

    def get_it_gb_nm_stats(self, campaign_id, set_sort_num):
        """메시지 생성시, 그룹 내 아이템 구분(복종)별 고객수 통계 조회를 위한 쿼리"""
        with self.db() as db:
            subquery = db.query(
                distinct(StyleMasterEntity.rep_nm).label("rep_nm"),
                StyleMasterEntity.it_gb_nm,
            ).subquery()

            return (
                db.query(
                    CampaignSetRecipientsEntity.group_sort_num,
                    subquery.c.it_gb_nm,
                    func.count(CampaignSetRecipientsEntity.cus_cd).label("cus_count"),
                )
                .join(subquery, CampaignSetRecipientsEntity.rep_nm == subquery.c.rep_nm)
                .filter(
                    CampaignSetRecipientsEntity.campaign_id == campaign_id,
                    CampaignSetRecipientsEntity.set_sort_num == set_sort_num,
                )
                .group_by(
                    CampaignSetRecipientsEntity.group_sort_num, subquery.c.it_gb_nm
                )
                .all()
            )

    def get_age_stats(self, campaign_id, set_sort_num):
        """메시지 생성시, 그룹 내 연령별 고객수 통계 조회를 위한 쿼리"""
        with self.db() as db:
            subquery = db.query(
                distinct(CustomerInfoStatusEntity.age).label("age_seg"),
                CustomerInfoStatusEntity.cus_cd,
            ).subquery()

            return (
                db.query(
                    CampaignSetRecipientsEntity.group_sort_num,
                    subquery.c.age_seg,
                    func.count(CampaignSetRecipientsEntity.cus_cd).label("cus_count"),
                )
                .join(subquery, CampaignSetRecipientsEntity.cus_cd == subquery.c.cus_cd)
                .filter(
                    CampaignSetRecipientsEntity.campaign_id == campaign_id,
                    CampaignSetRecipientsEntity.set_sort_num == set_sort_num,
                )
                .group_by(
                    CampaignSetRecipientsEntity.group_sort_num, subquery.c.age_seg
                )
                .all()
            )

    def get_campaign_messages(
        self, campaign_id, req_set_group_seqs
    ) -> list[CampaignMessages]:
        """캠페인의 메세지를 모두 조회하는 쿼리"""
        with self.db() as db:
            message_data = (
                db.query(
                    SetGroupMessagesEntity,
                    CampaignRemindEntity.remind_date,
                    CampaignRemindEntity.remind_duration,
                )
                .options(
                    joinedload(SetGroupMessagesEntity.kakao_button_links),
                    joinedload(SetGroupMessagesEntity.msg_resources),
                )
                .outerjoin(
                    CampaignRemindEntity,
                    and_(
                        SetGroupMessagesEntity.campaign_id
                        == CampaignRemindEntity.campaign_id,
                        SetGroupMessagesEntity.remind_step
                        == CampaignRemindEntity.remind_step,
                    ),
                )
                .filter(
                    SetGroupMessagesEntity.campaign_id == campaign_id,
                    SetGroupMessagesEntity.set_group_msg_seq.in_(req_set_group_seqs),
                )
                .all()
            )

        result = []
        for set_group_message, remind_date, remind_duration in message_data:
            set_group_message_model = SetGroupMessages.from_orm(set_group_message)
            message_md = CampaignMessages(
                set_group_message=set_group_message_model,
                remind_date=remind_date,
                remind_duration=remind_duration,
            )
            result.append(message_md)

        return result
