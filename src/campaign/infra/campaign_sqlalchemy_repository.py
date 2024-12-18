from sqlalchemy import Integer, and_, delete, desc, distinct, func, not_, or_, update
from sqlalchemy.orm import Session, joinedload

from src.audiences.enums.audience_status import AudienceStatus
from src.audiences.infra.entity.audience_entity import AudienceEntity
from src.audiences.infra.entity.audience_stats_entity import AudienceStatsEntity
from src.audiences.infra.entity.variable_table_list import CustomerInfoStatusEntity
from src.campaign.domain.campaign import Campaign
from src.campaign.domain.campaign_messages import CampaignMessages, SetGroupMessage
from src.campaign.domain.campaign_remind import CampaignRemind
from src.campaign.domain.campaign_timeline import CampaignTimeline
from src.campaign.domain.send_reservation import SendReservation
from src.campaign.enums.campagin_status import CampaignStatus
from src.campaign.enums.campaign_approval_status import CampaignApprovalStatus
from src.campaign.enums.send_type import SendType
from src.campaign.infra.dto.already_sent_campaign import AlreadySentCampaign
from src.campaign.infra.dto.campaign_reviewer_info import CampaignReviewerInfo
from src.campaign.infra.entity.approver_entity import ApproverEntity
from src.campaign.infra.entity.campaign_approval_entity import (
    CampaignApprovalEntity,
)
from src.campaign.infra.entity.campaign_entity import CampaignEntity
from src.campaign.infra.entity.campaign_remind_entity import CampaignRemindEntity
from src.campaign.infra.entity.campaign_set_groups_entity import CampaignSetGroupsEntity
from src.campaign.infra.entity.campaign_set_recipients_entity import (
    CampaignSetRecipientsEntity,
)
from src.campaign.infra.entity.campaign_sets_entity import CampaignSetsEntity
from src.campaign.infra.entity.campaign_timeline_entity import CampaignTimelineEntity
from src.campaign.infra.entity.coupon_custs import OfferCustEntity
from src.campaign.infra.entity.send_reservation_entity import SendReservationEntity
from src.campaign.infra.entity.set_group_messages_entity import SetGroupMessagesEntity
from src.common.sqlalchemy.object_access_condition import object_access_condition
from src.common.utils.string_utils import is_convertible_to_int
from src.offers.infra.entity.offers_entity import OffersEntity
from src.products.infra.entity.product_master_entity import ProductMasterEntity
from src.search.routes.dto.id_with_item_response import IdWithItem
from src.strategy.enums.strategy_status import StrategyStatus
from src.strategy.infra.entity.strategy_entity import StrategyEntity
from src.users.domain.user import User
from src.users.infra.entity.user_entity import UserEntity


class CampaignSqlAlchemy:

    def get_campaign_by_name(self, name: str, db: Session):
        return db.query(CampaignEntity).filter(CampaignEntity.campaign_name == name).first()

    def get_all_campaigns(
        self, start_date: str, end_date: str, user: User, db: Session
    ) -> list[Campaign]:

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

        campaigns = [Campaign.model_validate(entity) for entity in campaign_entities]

        return campaigns

    def is_existing_campaign_by_offer_event_no(self, offer_event_no, db: Session):

        used_event_no = (
            db.query(CampaignSetsEntity)
            .join(
                CampaignEntity,
                CampaignSetsEntity.campaign_id == CampaignEntity.campaign_id,
            )
            .filter(
                CampaignEntity.campaign_status_code.notin_(["o2", "s3"]),
                CampaignSetsEntity.coupon_no == offer_event_no,
            )
            .first()
        )

        if used_event_no is None:
            return False

        return True

    def get_campaign_by_strategy_id(self, strategy_id: str, db: Session) -> list[Campaign]:
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
                func.cast(CampaignTimelineEntity.created_by, Integer) == UserEntity.user_id,
            )
            .filter(
                CampaignTimelineEntity.campaign_id == campaign_id,
            )
            .order_by(desc(CampaignTimelineEntity.timeline_no))
            .all()
        )

        return [CampaignTimeline.model_validate(timeline) for timeline in timelines]

    def search_campaign(self, keyword, current_date, two_weeks_ago, db) -> list[IdWithItem]:
        conditions = []

        if keyword:
            modified_string = keyword.replace("cam-", "")
            keyword = f"%{keyword}%"

            if is_convertible_to_int(modified_string):
                conditions.append(CampaignEntity.campaign_id.ilike(keyword))  # audience_id
            else:
                conditions.append(CampaignEntity.campaign_name.ilike(keyword))  # audience_name

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
        self, campaign_id, req_set_group_seqs, db: Session
    ) -> SendReservation:
        return (
            db.query(SendReservationEntity)
            .filter(
                SendReservationEntity.campaign_id == campaign_id,
                SendReservationEntity.test_send_yn == "n",
                SendReservationEntity.set_group_msg_seq.in_(req_set_group_seqs),
                SendReservationEntity.send_resv_state.not_in(  # pyright: ignore [reportAttributeAccessIssue]
                    ["21", "01", "00"]
                ),  # 발송한 메세지 필터
            )
            .first()
        )

    def get_group_item_nm_stats(self, campaign_id, set_sort_num, db: Session):
        """
        item -> product_name
        """

        subquery = db.query(
            distinct(ProductMasterEntity.rep_nm).label("rep_nm"),
            ProductMasterEntity.product_name,
        ).subquery()

        return (
            db.query(
                CampaignSetRecipientsEntity.group_sort_num,
                subquery.c.product_name,
                func.count(CampaignSetRecipientsEntity.cus_cd).label("cus_count"),
            )
            .join(subquery, CampaignSetRecipientsEntity.rep_nm == subquery.c.rep_nm)
            .filter(
                CampaignSetRecipientsEntity.campaign_id == campaign_id,
                CampaignSetRecipientsEntity.set_sort_num == set_sort_num,
            )
            .group_by(CampaignSetRecipientsEntity.group_sort_num, subquery.c.product_name)
            .all()
        )

    def get_it_gb_nm_stats(self, campaign_id, set_sort_num, db: Session):
        """메시지 생성시, 그룹 내 아이템 구분(복종)별 고객수 통계 조회를 위한 쿼리

        it_gb -> brand_name
        테스트 데이터 :
        ALTOS  -> MOUNTAIN TEE(임시변경)
        PURO -> MOUNTAIN PANTS(임시변경)
        """

        subquery = db.query(
            distinct(ProductMasterEntity.rep_nm).label("rep_nm"),
            ProductMasterEntity.category_name,
        ).subquery()

        return (
            db.query(
                CampaignSetRecipientsEntity.group_sort_num,
                subquery.c.category_name,
                func.count(CampaignSetRecipientsEntity.cus_cd).label("cus_count"),
            )
            .join(subquery, CampaignSetRecipientsEntity.rep_nm == subquery.c.rep_nm)
            .filter(
                CampaignSetRecipientsEntity.campaign_id == campaign_id,
                CampaignSetRecipientsEntity.set_sort_num == set_sort_num,
            )
            .group_by(CampaignSetRecipientsEntity.group_sort_num, subquery.c.category_name)
            .all()
        )

    def get_age_stats(self, campaign_id, set_sort_num, db: Session):
        """메시지 생성시, 그룹 내 연령별 고객수 통계 조회를 위한 쿼리"""

        subquery = db.query(
            distinct(CustomerInfoStatusEntity.age_group_10).label("age_group_10"),
            CustomerInfoStatusEntity.cus_cd,
        ).subquery()

        return (
            db.query(
                CampaignSetRecipientsEntity.group_sort_num,
                subquery.c.age_group_10,
                func.count(CampaignSetRecipientsEntity.cus_cd).label("cus_count"),
            )
            .join(subquery, CampaignSetRecipientsEntity.cus_cd == subquery.c.cus_cd)
            .filter(
                CampaignSetRecipientsEntity.campaign_id == campaign_id,
                CampaignSetRecipientsEntity.set_sort_num == set_sort_num,
            )
            .group_by(CampaignSetRecipientsEntity.group_sort_num, subquery.c.age_group_10)
            .all()
        )

    def get_campaign_messages(
        self, campaign_id, req_set_group_seqs, db: Session
    ) -> list[CampaignMessages]:
        """캠페인의 메세지를 모두 조회하는 쿼리"""

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
                    SetGroupMessagesEntity.campaign_id == CampaignRemindEntity.campaign_id,
                    SetGroupMessagesEntity.remind_step == CampaignRemindEntity.remind_step,
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
            set_group_message_model = SetGroupMessage.from_orm(set_group_message)
            message_md = CampaignMessages(
                set_group_message=set_group_message_model,
                remind_date=remind_date,
                remind_duration=remind_duration,
            )
            result.append(message_md)

        return result

    def register_campaign(self, model: Campaign, db) -> Campaign:
        remind_entities = [
            CampaignRemindEntity(
                send_type_code=remind.send_type_code,
                remind_media=remind.remind_media,
                remind_step=remind.remind_step,
                remind_date=remind.remind_date,
                remind_duration=remind.remind_duration,
                created_by=model.created_by,
                updated_by=model.updated_by,
            )
            for remind in model.remind_list
        ]

        entity = CampaignEntity(
            campaign_name=model.campaign_name,
            budget=model.budget,
            campaign_type_code=model.campaign_type_code,
            campaign_type_name=model.campaign_type_name,
            medias=model.medias,
            campaign_status_group_code=model.campaign_status_group_code,
            campaign_status_group_name=model.campaign_status_group_name,
            campaign_status_code=model.campaign_status_code,
            campaign_status_name=model.campaign_status_name,
            send_type_code=model.send_type_code,
            send_type_name=model.send_type_name,
            repeat_type=model.repeat_type,
            week_days=model.week_days,
            send_date=model.send_date,
            is_msg_creation_recurred=model.is_msg_creation_recurred,
            is_approval_recurred=model.is_approval_recurred,
            datetosend=str(model.datetosend) if model.datetosend else None,
            timetosend=model.timetosend,
            start_date=model.start_date,
            end_date=model.end_date,
            group_end_date=model.group_end_date,
            has_remind=model.has_remind,
            campaigns_exc=model.campaigns_exc,
            audiences_exc=model.audiences_exc,
            strategy_id=model.strategy_id,
            strategy_theme_ids=model.strategy_theme_ids,
            is_personalized=model.is_personalized,
            progress=model.progress,
            msg_delivery_vendor=model.msg_delivery_vendor,
            shop_send_yn=model.shop_send_yn,
            retention_day=model.retention_day,
            owned_by_dept=model.owned_by_dept,
            owned_by_dept_name=model.owned_by_dept_name,
            owned_by_dept_abb_name=model.owned_by_dept_abb_name,
            created_by_name=model.created_by_name,
            created_by=model.created_by,
            updated_by=model.updated_by,
            remind_list=remind_entities,
        )

        db.add(entity)
        db.flush()

        return Campaign.model_validate(entity)

    def save_timeline(self, timeline: CampaignTimeline, db: Session):
        entity = CampaignTimelineEntity(
            timeline_type=timeline.timeline_type,
            campaign_id=timeline.campaign_id,
            description=timeline.description,
            status_no=timeline.status_no,
            created_by=timeline.created_by,
            created_by_name=timeline.created_by_name,
        )
        db.add(entity)
        db.flush()

    def get_campaign_sets(self, campaign_id: str, db: Session):
        entities = (
            db.query(
                CampaignSetsEntity.set_seq,
                CampaignSetsEntity.set_sort_num,
                CampaignSetsEntity.is_group_added,
                CampaignSetsEntity.strategy_theme_id,
                CampaignSetsEntity.strategy_theme_name,
                CampaignSetsEntity.recsys_model_id,
                CampaignSetsEntity.audience_id,
                CampaignSetsEntity.audience_name,
                AudienceStatsEntity.audience_count,
                AudienceStatsEntity.audience_portion,
                AudienceStatsEntity.audience_unit_price,
                AudienceStatsEntity.response_rate,
                CampaignSetsEntity.coupon_no,
                CampaignSetsEntity.coupon_name,
                CampaignSetsEntity.recipient_count,
                CampaignSetsEntity.medias,
                CampaignSetsEntity.media_cost,
                CampaignSetsEntity.is_confirmed,
                CampaignSetsEntity.is_message_confirmed,
            )
            .outerjoin(
                AudienceStatsEntity,
                CampaignSetsEntity.audience_id == AudienceStatsEntity.audience_id,
            )
            .filter(CampaignSetsEntity.campaign_id == campaign_id)
        )
        return entities

    def get_campaign_set_groups(self, campaign_id: str, db: Session):
        entities = (
            db.query(CampaignSetGroupsEntity)
            .filter(CampaignSetGroupsEntity.campaign_id == campaign_id)
            .all()
        )
        return entities

    def get_campaign_detail(self, campaign_id, user, db: Session) -> Campaign:
        entity = db.query(CampaignEntity).filter(CampaignEntity.campaign_id == campaign_id).first()
        return Campaign.model_validate(entity)

    def get_campaign_remind(self, campaign_id: str, db: Session) -> list[CampaignRemind]:
        entities = (
            db.query(CampaignRemindEntity)
            .filter(CampaignRemindEntity.campaign_id == campaign_id)
            .order_by(CampaignRemindEntity.remind_step)
            .all()
        )

        return [CampaignRemind.model_validate(entity) for entity in entities]

    def get_campaign_reviewers(self, campaign_id: str, db: Session) -> list[CampaignReviewerInfo]:

        entities = (
            db.query(
                CampaignApprovalEntity.approval_no,
                ApproverEntity.user_id,
                ApproverEntity.user_name,
                ApproverEntity.is_approved,
                ApproverEntity.department_abb_name,
                UserEntity.test_callback_number,
                ApproverEntity.is_approved,
            )
            .join(ApproverEntity, CampaignApprovalEntity.approval_no == ApproverEntity.approval_no)
            .outerjoin(UserEntity, ApproverEntity.user_id == UserEntity.user_id)
            .filter(
                and_(
                    CampaignApprovalEntity.campaign_id == campaign_id,
                    or_(
                        CampaignApprovalEntity.approval_status
                        == CampaignApprovalStatus.REVIEW.value,  # 수정요청 받은 결재의 승인자
                        CampaignApprovalEntity.approval_status
                        == CampaignApprovalStatus.APPROVED.value,  # 승인된 결재의 승인자
                    ),
                )
            )
            .all()
        )

        return [CampaignReviewerInfo.model_validate(entity) for entity in entities]

    def update_campaign_progress_status(self, campaign_id, update_status: str, db: Session):
        update_statement = (
            update(CampaignEntity)
            .where(CampaignEntity.campaign_id == campaign_id)
            .values(progress=update_status)
        )
        db.execute(update_statement)

    def get_campaign_set_group_message(
        self, campaign_id, set_group_msg_seq, db: Session
    ) -> SetGroupMessage:

        entity = (
            db.query(SetGroupMessagesEntity)
            .filter(
                SetGroupMessagesEntity.set_group_msg_seq == set_group_msg_seq,
                SetGroupMessagesEntity.campaign_id == campaign_id,
            )
            .first()
        )

        return SetGroupMessage.model_validate(entity)

    def get_message_in_send_reservation(
        self, campaign_id, set_group_msg_seq, db
    ) -> SendReservation | None:
        send_msg_first = (
            db.query(SendReservationEntity)
            .filter(
                SendReservationEntity.campaign_id == campaign_id,
                SendReservationEntity.test_send_yn == "n",
                SendReservationEntity.set_group_msg_seq == set_group_msg_seq,
                SendReservationEntity.send_resv_state.not_in(
                    ["21", "01", "00"]
                ),  # 발송한 메세지 필터
            )
            .first()
        )

        if send_msg_first is None:
            return None

        return SendReservation.model_validate(send_msg_first)

    def update_campaign_set_group_message_type(
        self, campaign_id, set_group_seq, message_type, db: Session
    ):
        update_statement = (
            update(CampaignSetGroupsEntity)
            .where(
                and_(
                    CampaignSetGroupsEntity.campaign_id == campaign_id,
                    CampaignSetGroupsEntity.set_group_seq == set_group_seq,
                )
            )
            .values(msg_type=message_type)
        )
        db.execute(update_statement)

    def delete_campaign(self, campaign, db: Session):
        campaign_id = campaign.campaign_id
        strategy_id = campaign.strategy_id

        select_query = db.query(CampaignEntity).filter(
            ~(CampaignEntity.campaign_id == campaign_id)
            & (CampaignEntity.strategy_id == strategy_id)
            & (CampaignEntity.campaign_status_code.not_in(["o2", "s3"]))  # 미완료 캠페인
        )
        strategy_exist = db.query(select_query.exists()).scalar()

        # 오디언스 상태변경 체크
        set_aud_query = (
            db.query(func.distinct(CampaignSetsEntity.audience_id))
            .filter(CampaignSetsEntity.campaign_id == campaign_id)
            .all()
        )
        aud_lst = [aud[0] for aud in set_aud_query]
        select_aud_query = (
            db.query(func.distinct(CampaignSetsEntity.audience_id))
            .join(CampaignEntity, CampaignSetsEntity.campaign_id == CampaignEntity.campaign_id)
            .filter(
                ~(CampaignSetsEntity.campaign_id == campaign_id)  # 다른 캠페인에서도 사용
                & (CampaignSetsEntity.audience_id.in_(aud_lst))  # 삭제하는 캠페인 오디언스
                & (CampaignEntity.campaign_status_code.not_in(["o2", "s3"]))  # 미완료 캠페인
            )
        )
        aud_active_to_lst = [aud[0] for aud in select_aud_query]
        aud_delete_to_lst = [aud for aud in aud_lst if aud not in aud_active_to_lst]

        # Offers 에 campaign_id 지우기
        set_event_no_lst = (
            db.query(CampaignSetsEntity.coupon_no)
            .filter(
                CampaignSetsEntity.campaign_id == campaign_id, CampaignSetsEntity.coupon_no != None
            )
            .all()
        )

        for evnt_obj in set_event_no_lst:
            db.query(OffersEntity).filter(
                OffersEntity.coupon_no == evnt_obj.coupon_no,
            ).update({"campaign_id": None})

        # Campaign 관련 엔티티 삭제
        self._delete_entity_related_to_campaign(campaign_id, db)

        # Strategy 상태변경 실행
        if strategy_exist is False:
            db.query(StrategyEntity).filter(StrategyEntity.strategy_id == strategy_id).update(
                {
                    "strategy_status_code": StrategyStatus.inactive.value,
                    "strategy_status_name": StrategyStatus.inactive.description,
                }
            )
            db.commit()

        if len(aud_delete_to_lst) > 0:
            db.query(AudienceEntity).filter(
                AudienceEntity.audience_id.in_(aud_delete_to_lst)
            ).update(
                {
                    "audience_status_code": AudienceStatus.inactive.value,
                    "audience_status_name": AudienceStatus.inactive.description,
                }
            )
            db.commit()

    def _delete_entity_related_to_campaign(self, campaign_id, db: Session):
        # campaign_object
        deleted_obj = (
            db.query(CampaignEntity).filter(CampaignEntity.campaign_id == campaign_id).first()
        )

        db.delete(deleted_obj)

        # recipients
        delete_statement = delete(CampaignSetRecipientsEntity).where(
            CampaignSetRecipientsEntity.campaign_id == campaign_id
        )

        db.execute(delete_statement)

        # approvers
        delete_statement = delete(ApproverEntity).where(ApproverEntity.campaign_id == campaign_id)

        db.execute(delete_statement)

        # campaign_approvals, campaign_status_history
        deleted_objs = (
            db.query(CampaignApprovalEntity)
            .filter(CampaignApprovalEntity.campaign_id == campaign_id)
            .all()
        )

        for elem in deleted_objs:
            deleted_obj = (
                db.query(CampaignApprovalEntity)
                .filter(CampaignApprovalEntity.approval_no == elem.approval_no)
                .first()
            )

            db.delete(deleted_obj)

        # campaign_timeline
        delete_statement = delete(CampaignTimelineEntity).where(
            CampaignTimelineEntity.campaign_id == campaign_id
        )

        db.execute(delete_statement)

        # send_reservation
        delete_statement = delete(SendReservationEntity).where(
            SendReservationEntity.campaign_id == campaign_id
        )

        db.execute(delete_statement)

        # offer_custs
        delete_statement = delete(OfferCustEntity).where(OfferCustEntity.campaign_id == campaign_id)

        db.execute(delete_statement)

    def update_send_reservation_status_to_success(self, refkey, db: Session):
        update_statement = (
            update(SendReservationEntity)
            .where(SendReservationEntity.send_resv_seq == refkey)
            .values(sent_success="y", send_resv_state="02")
        )

        db.execute(update_statement)

    def update_send_reservation_status_to_failure(self, refkey, db: Session):
        update_statement = (
            update(SendReservationEntity)
            .where(SendReservationEntity.send_resv_seq == refkey)
            .values(send_resv_state="41")
        )

        db.execute(update_statement)

    def get_already_sent_campaigns(self, campaign_id, db) -> list[AlreadySentCampaign]:
        already_sent_campaigns = (
            db.query(
                SendReservationEntity.campaign_id,
                SendReservationEntity.msg_category,
                SendReservationEntity.remind_step,
            )
            .distinct(
                SendReservationEntity.campaign_id,
                SendReservationEntity.msg_category,
                SendReservationEntity.remind_step,
            )
            .where(
                and_(
                    SendReservationEntity.campaign_id == campaign_id,
                    SendReservationEntity.test_send_yn == "n",
                    SendReservationEntity.send_resv_state != "00",
                )
            )
            .all()
        )

        return [
            AlreadySentCampaign(
                campaign_id=campaign.campaign_id,
                msg_category=campaign.msg_category,
                remind_step=campaign.remind_step,
            )
            for campaign in already_sent_campaigns
        ]
