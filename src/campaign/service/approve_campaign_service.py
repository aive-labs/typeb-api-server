import logging
from datetime import datetime, timedelta, timezone

import numpy as np
import pandas as pd
import pytz
from fastapi import HTTPException
from sqlalchemy import and_, delete, desc, func, update
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session
from sqlalchemy.sql.functions import coalesce

from src.campaign.enums.campaign_approval_status import CampaignApprovalStatus
from src.campaign.enums.campaign_timeline_type import CampaignTimelineType
from src.campaign.infra.entity.approver_entity import ApproverEntity
from src.campaign.infra.entity.campaign_approval_entity import CampaignApprovalEntity
from src.campaign.infra.entity.campaign_credit_payment_entity import (
    CampaignCreditPaymentEntity,
)
from src.campaign.infra.entity.campaign_entity import CampaignEntity
from src.campaign.infra.entity.campaign_set_groups_entity import CampaignSetGroupsEntity
from src.campaign.infra.entity.campaign_set_recipients_entity import (
    CampaignSetRecipientsEntity,
)
from src.campaign.infra.entity.campaign_sets_entity import CampaignSetsEntity
from src.campaign.infra.entity.campaign_status_history_entity import (
    CampaignStatusHistoryEntity,
)
from src.campaign.infra.entity.campaign_timeline_entity import CampaignTimelineEntity
from src.campaign.infra.entity.send_dag_log_entity import SendDagLogEntity
from src.campaign.infra.entity.send_reservation_entity import SendReservationEntity
from src.campaign.infra.entity.set_group_messages_entity import SetGroupMessagesEntity
from src.campaign.infra.sqlalchemy_query.convert_to_button_format import (
    convert_to_button_format,
)
from src.campaign.infra.sqlalchemy_query.get_message_resources import (
    get_message_resources,
)
from src.campaign.infra.sqlalchemy_query.modify_reservation_sync_service import (
    ModifyReservSync,
)
from src.campaign.infra.sqlalchemy_query.personal_variable_formatting import (
    personal_variable_formatting,
)
from src.campaign.routes.port.approve_campaign_usecase import ApproveCampaignUseCase
from src.campaign.service.port.base_campaign_repository import BaseCampaignRepository
from src.campaign.service.port.base_campaign_set_repository import (
    BaseCampaignSetRepository,
)
from src.campaign.utils.campagin_status_utils import *
from src.campaign.utils.convert_by_message_format import convert_by_message_format
from src.common.enums.message_delivery_vendor import MsgDeliveryVendorEnum
from src.common.infra.entity.customer_master_entity import CustomerMasterEntity
from src.common.sqlalchemy.object_access_condition import object_access_condition
from src.common.timezone_setting import selected_timezone
from src.common.utils.data_converter import DataConverter
from src.common.utils.date_utils import (
    create_logical_date_for_airflow,
    get_korean_current_datetime_yyyymmddhh24mims,
    get_unix_timestamp,
    localtime_converter,
)
from src.contents.infra.entity.contents_entity import ContentsEntity
from src.core.exceptions.exceptions import (
    ConsistencyException,
    DuplicatedException,
    NotFoundException,
    PolicyException,
)
from src.core.transactional import transactional
from src.message_template.infra.entity.message_template_entity import (
    MessageTemplateEntity,
)
from src.messages.service.message_reserve_controller import MessageReserveController
from src.offers.infra.entity.offers_entity import OffersEntity
from src.payment.domain.credit_history import CreditHistory
from src.payment.enum.credit_status import CreditStatus
from src.payment.infra.entity.remaining_credit_entity import RemainingCreditEntity
from src.payment.service.port.base_credit_repository import BaseCreditRepository
from src.users.domain.user import User
from src.users.infra.entity.user_entity import UserEntity


class ApproveCampaignService(ApproveCampaignUseCase):

    def __init__(
        self,
        campaign_repository: BaseCampaignRepository,
        campaign_set_repository: BaseCampaignSetRepository,
        credit_repository: BaseCreditRepository,
    ):
        self.campaign_repository = campaign_repository
        self.campaign_set_repository = campaign_set_repository
        self.credit_repository = credit_repository
        self.message_controller = MessageReserveController()

    @transactional
    async def exec(
        self,
        campaign_id,
        to_status,
        user: User,
        db: Session,
        reviewers: str | None = None,
    ) -> dict:
        """
        캠페인 상태 변경 API

        - 캠페인 상태로그 : campaign_status_history
        - 리뷰 요청
            - 캠페인 승인 : campaign_approvals
            - 승인자 : approvers
        - 캠페인 타임라인 인서트 : campaign_timeline

        - campaign-dag : to_status (o1 운영중, o2 완료, s3 기간만료)
        """
        user_id = str(user.user_id)
        created_at = localtime_converter()
        datetime_obj = datetime.fromisoformat(created_at)
        today = datetime_obj.strftime("%Y%m%d")

        old_campaign = self.check_permission_to_change_status(campaign_id, db, user)
        remind_list = old_campaign.remind_list

        # 캠페인 셋에서 media_cost를 통해 매체 비용을 계산한다.
        campaign_cost = self.campaign_set_repository.get_campaign_cost_by_campaign_id(
            campaign_id, db
        )

        # 변경전 캠페인 상태
        from_status = old_campaign.campaign_status_code
        send_date = old_campaign.send_date if old_campaign.send_date else old_campaign.start_date

        # 초기값
        approval_time_log_skip = False
        approval_excute = False

        # 승인 요청
        if is_status_tempsave_to_review(from_status, to_status):

            self.check_send_date_after_approval_date(send_date, today)

            approval_no = self.save_campaign_approval(campaign_id, created_at, db, user, user_id)

            # 캠페인 승인자 테이블 저장
            if reviewers:
                reviewer_ids = [int(user_id) for user_id in reviewers.split(",")]
            else:
                reviewer_ids = []

            reviewer_entities = (
                db.query(UserEntity).filter(UserEntity.user_id.in_(reviewer_ids)).all()
            )

            for user in reviewer_entities:
                self.save_approver(approval_no, campaign_id, created_at, db, user, user_id)

        # 승인 거절: 승인자 중 한명이라도 거절했을 경우, 해당 승인 건은 무효. 캠페인 상태는 임시저장 상태로 변경
        elif is_status_review_to_tempsave(from_status, to_status):

            # 현재 승인거절이 가능한 유효힌 approval_no의 reviewer 가져오기
            reviewer_ids = self.get_reviewer_ids(campaign_id, db)

            # 해당 id에 속하는 사용자가 승인 권한이 있는지 확인
            self.check_permission_to_approve_by_user_id(reviewer_ids, user)

            # 승인 거절하기
            # 캠페인의 review 상태의 결재 건이 하나만 존재하는 것이 전제되어야함
            approval_status = CampaignApprovalStatus.REVIEW.value
            approval_obj = self.get_campaign_approval_obj(db, campaign_id, approval_status)
            if not approval_obj:
                raise NotFoundException(detail={"message": "승인 정보를 찾지 못했습니다."})

            approval_obj.approval_status = CampaignApprovalStatus.REJECTED.value  # 해당 캠페인 무효
            approval_no = approval_obj.approval_no

            # 승인 거절 : 캠페인 타임라인 로그
            self.save_campaign_logs(
                db=db,
                campaign_id=campaign_id,
                timeline_type="approval",
                created_at=created_at,
                created_by=user_id,
                created_by_name=user.username,
                to_status=to_status,
                status_no=None,
            )

        # 리뷰중 -> 진행대기 : "승인"
        elif is_status_review_to_pending(from_status, to_status):

            # 1. 일단 기존에 결제 기록이 있으면 환불 진행(무조건 0건 또는 1건 존재)
            campaign_credit_entity = (
                db.query(CampaignCreditPaymentEntity)
                .filter(CampaignCreditPaymentEntity.campaign_id == campaign_id)
                .first()
            )

            if campaign_credit_entity:
                remaining_amount = self.credit_repository.get_remain_credit(db)

                # 환불 금액
                refund_cost = campaign_credit_entity.cost

                # 2. 크레딧 히스토리에 환불 기록
                refund_credit_history = CreditHistory(
                    user_name=user.username,
                    description=f"캠페인({campaign_id}) 수정으로 인한 크레딧 사용 취소",
                    status=CreditStatus.REFUND.value,
                    charge_amount=refund_cost,
                    remaining_amount=remaining_amount + refund_cost,
                    created_by=str(user.user_id),
                    updated_by=str(user.user_id),
                )
                self.credit_repository.add_history(refund_credit_history, db)

                # 3. 잔여 크레딧 테이블에 환불 크레딧 합산
                self.credit_repository.update_credit(refund_cost, db)

            # 잔여 크레딧이 충분한지 확인
            credit_entity = db.query(RemainingCreditEntity).first()
            if credit_entity is None:
                raise ConsistencyException(detail={"message": "크레딧 정보가 존재하지 않습니다."})

            remaining_credit = credit_entity.remaining_credit

            if remaining_credit < campaign_cost:
                raise PolicyException(
                    detail={
                        "code": "campaign/credit/insufficient",
                        "message": "크레딧이 부족합니다. 크레딧을 충전해주세요.",
                        "remaining_credit": remaining_credit,
                        "campaign_cost": campaign_cost,
                    }
                )

            # 결제 진행
            # 1. credit_history에 저장
            new_credit_history = CreditHistory(
                user_name=user.username,
                description=f"캠페인 집행({campaign_id})",
                status=CreditStatus.USE.value,
                use_amount=campaign_cost,
                remaining_amount=remaining_credit - campaign_cost,
                note=f"캠페인 리마인드 {len(remind_list)}건 포함" if len(remind_list) > 0 else None,
                created_by=str(user.user_id),
                updated_by=str(user.user_id),
            )
            self.credit_repository.add_history(new_credit_history, db)

            # 2. remaining_credit 차감
            self.credit_repository.update_credit(-campaign_cost, db)

            # 3. campaign_credit_payment 테이블 저장
            # 기존 레코드가 있으면 업데이트하고, 없으면 삽입하는 쿼리
            insert_stmt = insert(CampaignCreditPaymentEntity).values(
                campaign_id=campaign_id,
                cost=campaign_cost,
                created_by=str(user.user_id),
                updated_by=str(user.user_id),
            )

            # campaign_id가 이미 존재하면 cost와 updated_by를 업데이트
            update_stmt = insert_stmt.on_conflict_do_update(
                index_elements=["campaign_id"],
                set_={"cost": campaign_cost, "updated_by": str(user.user_id)},
            )
            db.execute(update_stmt)

            # 현재 승인이 가능한 유효힌 approval_no의 reviewer 가져오기
            reviewer_ids = self.get_reviewer_ids(campaign_id, db)

            # 해당 id에 속하는 사용자가 승인 권한이 있는지 확인
            self.check_permission_to_approve_by_user_id(reviewer_ids, user)

            # 해당 승인 오브젝트 조회
            approval_status = CampaignApprovalStatus.REVIEW.value
            approval_obj = self.get_campaign_approval_obj(db, campaign_id, approval_status)
            if not approval_obj:
                raise NotFoundException(detail={"message": "승인 정보를 찾지 못했습니다."})
            approval_no = approval_obj.approval_no

            if len(reviewer_ids) == 1 and user.user_id == int(reviewer_ids[0]):

                # 본인을 제외한 다른 리뷰어가 모두 승인했는 경우, 해당 승인 건을 승인 처리하기
                approval_obj.approval_status = CampaignApprovalStatus.APPROVED.value

                # 리뷰어의 승인여부 업데이트하기
                self.approve_campaign_review(db, campaign_id, approval_no, user_id)

                # 승인 처리
                self.save_campaign_logs(
                    db=db,
                    campaign_id=campaign_id,
                    timeline_type="approval",
                    created_at=created_at,
                    created_by=user_id,
                    created_by_name=user.username,
                    to_status=to_status,  # 분기처리에 필요한 값. 타임로그에는 저장 x
                    status_no=None,
                )

                # 캠페인 승인 완료
                approval_excute = True
                self.save_campaign_logs(
                    db=db,
                    campaign_id=campaign_id,
                    timeline_type="approval",
                    created_at=created_at,
                    created_by=user_id,
                    created_by_name=user.username,
                    to_status=to_status,  # 분기처리에 필요한 값. 타임로그에는 저장 x
                    status_no=None,
                    approval_excute=approval_excute,
                )
            else:
                # 모든 리뷰어가 승인 완료되지 않아 캠페인 상태를 review로 유지
                # to-do: timeline_description
                to_status = CampaignStatus.review.value  # 상태변경 x (w1 -> w1)
                approval_time_log_skip = True

                # 리뷰어의 승인여부 업데이트하기
                self.approve_campaign_review(db, campaign_id, approval_no, user.user_id)

                # 승인 처리
                self.save_campaign_logs(
                    db=db,
                    campaign_id=campaign_id,
                    timeline_type="approval",
                    created_at=created_at,
                    created_by=user_id,
                    created_by_name=user.username,
                    to_status=to_status,  # 분기처리에 필요한 값. 타임로그에는 저장 x
                    status_no=None,
                )

        else:
            # 승인 처리 외 상태변경
            approval_no = await self.status_general_change(
                db, user, from_status, to_status, campaign_id
            )

        # 캠페인 상태 변경
        campaign_status = CampaignStatus.get_eums()
        campaign_status_input = [
            (i["_value_"], i["description"], i["group"], i["group_description"])
            for i in campaign_status
            if i["_value_"] == to_status
        ][0]

        old_campaign.campaign_status_code = campaign_status_input[0]
        old_campaign.campaign_status_name = campaign_status_input[1]
        old_campaign.campaign_status_group_code = campaign_status_input[2]
        old_campaign.campaign_status_group_name = campaign_status_input[3]

        status_hist = CampaignStatusHistoryEntity(
            campaign_id=campaign_id,
            from_status=from_status,
            to_status=to_status,
            created_at=created_at,
            approval_no=approval_no,  # if approval_no 초기값은 None
            created_by=user_id,
        )

        db.add(status_hist)

        db.flush()
        status_no = status_hist.status_no  # 캠페인 상태 번호

        if not approval_time_log_skip:
            # 일부 승인자 승인 후 캠페인 상태가 변경하지 않은 경우, 타임로그에 표시하지 않는다. ex) w1 -> w1
            # 캠페인 타임라인 로그 저장
            self.save_campaign_logs(
                db=db,
                campaign_id=campaign_id,
                timeline_type=CampaignTimelineType.STATUS_CHANGE.value,
                created_at=created_at,
                created_by=user.user_id,
                created_by_name=user.username,
                to_status=to_status,
                status_no=status_no,
            )
        db.flush()

        # 승인이 모두 완료 되어서 캠페인 진행대기 단계이면서 발송일자가 당일인 경우
        # 일회성 캠페인의 경우?
        if (to_status == "w2") and (approval_excute is True) and (send_date == today):

            # 캠페인 상태를 "운영중"으로 변경
            campaign = (
                db.query(CampaignEntity).filter(CampaignEntity.campaign_id == campaign_id).first()
            )
            if not campaign:
                raise NotFoundException(detail={"message": "캠페인 정보를 찾지 못했습니다."})

            campaign.campaign_status_code = "o1"
            campaign.campaign_status_name = "운영중"
            campaign.campaign_status_group_code = "o"
            campaign.campaign_status_group_name = "운영단계"

            print("1111")
            # 발송 예약
            send_reservation_result = await self.today_approval_campaign_execute(
                db,
                from_status=CampaignStatus.pending.value,
                to_status=CampaignStatus.ongoing.value,
                campaign_id=campaign_id,
                created_at=created_at,
                created_by=user_id,
                created_by_name=user.username,
                user=user,
                send_date=campaign.send_date,
                send_time=campaign.timetosend,
                approval_no=approval_no,
            )

            if send_reservation_result is False:
                txt = f"{campaign_id} : 당일 발송할 정상 예약 메세지가 존재하지 않습니다."
                return {"result": txt}

        db.commit()
        return {"res": "success"}

    def save_approver(self, approval_no, campaign_id, created_at, db, user, user_id):
        approver_entity = ApproverEntity(
            campaign_id=campaign_id,
            approval_no=approval_no,
            user_id=user.user_id,
            user_name=user.username,
            department_id=user.department_id,
            department_name=user.department_name,
            department_abb_name=user.department_abb_name,
            is_approved=False,  # 기초값 False
            created_at=created_at,
            created_by=user_id,
            updated_at=created_at,
            updated_by=user_id,
        )
        db.add(approver_entity)

    def save_campaign_approval(self, campaign_id, created_at, db, user, user_id):
        # 캠페인 승인 테이블 저장
        new_approver = CampaignApprovalEntity(
            campaign_id=campaign_id,
            requester=user.user_id,
            approval_status=CampaignApprovalStatus.REVIEW.value,  # 이 예시에서는 상태를 'REVIEW'로 가정
            created_at=created_at,
            created_by=user_id,
            updated_at=created_at,  # 생성 시점에 updated_at도 설정
            updated_by=user_id,
        )
        db.add(new_approver)
        # 캠페인 승인번호
        db.flush()
        approval_no = new_approver.approval_no
        return approval_no

    def get_reviewer_ids(self, campaign_id, db):
        approvers = self.get_campaign_approvers_to_review(db, campaign_id)
        reviewer_ids = [row._asdict()["user_id"] for row in approvers]
        return reviewer_ids

    def check_permission_to_approve_by_user_id(self, reviewer_ids, user):
        if user.user_id not in reviewer_ids:
            raise PolicyException(
                detail={
                    "code": "campaign/approval/denied/01",
                    "message": "승인 권한이 존재하지 않습니다.",
                },
            )

    def check_permission_to_change_status(self, campaign_id, db, user_obj):
        condition = object_access_condition(db, user_obj, CampaignEntity)
        campaign = (
            db.query(CampaignEntity)
            .filter(CampaignEntity.campaign_id == campaign_id, *condition)
            .first()
        )
        if not campaign:
            raise PolicyException(
                detail={
                    "code": "campaign/status/denied/access",
                    "message": "상태 변경 권한이 존재하지 않습니다.",
                },
            )
        return campaign

    def check_send_date_after_approval_date(self, send_date, today):
        if today > send_date:
            raise PolicyException(
                detail={
                    "code": "campaign/status/denied/access",
                    "message": f"발송일자는 승인일 이후만 가능합니다. 발송일자를 변경해주세요. (현재 메시지 발송일자: {send_date})",
                },
            )

    def save_campaign_logs(
        self,
        db,
        campaign_id,
        timeline_type,
        created_at,
        created_by,
        created_by_name,
        to_status=None,
        status_no=None,
        description=None,
        approval_excute=False,
        remind_step: int | None = None,
    ) -> bool:

        if timeline_type == CampaignTimelineType.APPROVAL.value:

            if to_status == CampaignStatus.review.value:
                description = f"{created_by_name} 승인 요청"

            elif to_status == CampaignStatus.pending.value and approval_excute is False:
                description = f"{created_by_name} 승인 처리"

            elif to_status == CampaignStatus.pending.value and approval_excute is True:
                description = "캠페인 승인 완료"

            elif to_status == CampaignStatus.tempsave.value:
                description = f"{created_by_name} 승인 거절"

            else:
                raise ValueError("Invalid campagin status")

        elif timeline_type == CampaignTimelineType.STATUS_CHANGE.value:
            description = to_status

        elif timeline_type == CampaignTimelineType.CAMPAIGN_EVENT.value:
            # 캠페인 시작, 캠페인 종료, ...
            description = description

        elif timeline_type == CampaignTimelineType.SEND_REQUEST.value:
            description = description

        elif timeline_type == CampaignTimelineType.HALT_MSG.value:
            description = description

        else:
            pass

        # 캠페인 타임라인 테이블 저장
        timelines = CampaignTimelineEntity(
            timeline_type=timeline_type,
            campaign_id=campaign_id,
            description=description,
            status_no=status_no,
            created_at=created_at,
            created_by=created_by,
            created_by_name=created_by_name,
        )

        db.add(timelines)

        return True

    def get_campaign_approvers_to_review(self, db: Session, campaign_id: str):
        return (
            db.query(
                CampaignApprovalEntity.approval_no,
                ApproverEntity.user_id,
                ApproverEntity.is_approved,
            )
            .join(ApproverEntity, CampaignApprovalEntity.approval_no == ApproverEntity.approval_no)
            .filter(
                CampaignApprovalEntity.campaign_id == campaign_id,
                CampaignApprovalEntity.approval_status == CampaignApprovalStatus.REVIEW.value,
                ApproverEntity.is_approved == False,  # 승인안한 리뷰어 오브젝트만 추출함
            )
            .all()
        )

    def get_campaign_approval_obj(self, db: Session, campaign_id: str, approval_status: str):

        base_obj = db.query(CampaignApprovalEntity).filter(
            CampaignApprovalEntity.campaign_id == campaign_id,
            CampaignApprovalEntity.approval_status == approval_status,
        )

        if approval_status in (CampaignApprovalStatus.REVIEW.value):
            return base_obj.first()

        else:
            return base_obj.order_by(desc(CampaignApprovalEntity.approval_no)).first()

    def approve_campaign_review(self, db: Session, campaign_id: str, approval_no: int, user_id):

        approver = (
            db.query(ApproverEntity)
            .filter(
                ApproverEntity.campaign_id == campaign_id,
                ApproverEntity.approval_no == approval_no,
                ApproverEntity.user_id == int(user_id),
            )
            .first()
        )

        if not approver:
            raise NotFoundException(detail={"message": "승인 정보를 찾지 못했습니다."})

        approver.is_approved = True

    async def status_general_change(self, db, user, from_status, to_status, campaign_id):
        print(f"status_general_change: {from_status} {to_status}")
        tz = "Asia/Seoul"
        korea_timezone = pytz.timezone(tz)
        current_korea_timestamp = datetime.now(korea_timezone)
        current_korea_date = current_korea_timestamp.strftime("%Y%m%d")
        current_korea_timestamp_plus_5_minutes = current_korea_timestamp + timedelta(minutes=5)

        if is_status_pending_to_haltbefore(from_status, to_status):
            # w2(캠페인 진행대기) -> s1(일시중지)
            # 진행대기 -> 일시중지 (00상태의 row 예약 상태 변경 "21")
            approval_no = self.get_campaign_approval_no(campaign_id, db)

            # 발송 취소 로깅
            created_at = localtime_converter()
            self.save_campaign_logs(
                db=db,
                campaign_id=campaign_id,
                timeline_type="halt_msg",
                created_at=created_at,
                created_by=user.user_id,
                created_by_name=user.username,
                description="캠페인 일시 정지",
            )

            update_pending_to_haltbefore = (
                update(SendReservationEntity)
                .where(
                    and_(
                        SendReservationEntity.campaign_id == campaign_id,
                        SendReservationEntity.send_sv_type == MsgDeliveryVendorEnum.DAU.value,
                        SendReservationEntity.test_send_yn == "n",
                    )
                )
                .values(
                    {
                        "send_resv_state": "21",
                        "log_comment": "캠페인이 일시중지 되었습니다.",
                        "log_date": created_at,
                        "update_resv_date": created_at,
                    }
                )
            )
            db.execute(update_pending_to_haltbefore)

            # 잔여 크레딧
            remaining_amount = self.credit_repository.get_remain_credit(db)
            # 환불 금액
            campaign_cost = self.campaign_set_repository.get_campaign_cost_by_campaign_id(
                campaign_id, db
            )

            # 크레딧 히스토리에 환불 기록
            refund_credit_history = CreditHistory(
                user_name=user.username,
                description=f"캠페인({campaign_id}) 일시중지로 인한 크레딧 사용 취소",
                status=CreditStatus.REFUND.value,
                charge_amount=campaign_cost,
                remaining_amount=remaining_amount + campaign_cost,
                created_by=str(user.user_id),
                updated_by=str(user.user_id),
            )
            self.credit_repository.add_history(refund_credit_history, db)

            # 잔여 크레딧 테이블에 환불 크레딧 합산
            self.credit_repository.update_credit(campaign_cost, db)

        elif is_status_pending_to_ongoing(from_status, to_status):
            # 진행대기(PENDING) -> 운영(ONGOING)
            approval_no = self.get_campaign_approval_no(campaign_id, db)

            created_at = localtime_converter()
            self.save_campaign_logs(
                db=db,
                campaign_id=campaign_id,
                timeline_type="campaign_event",
                created_at=created_at,
                created_by=user.user_id,
                created_by_name=user.username,
                description="캠페인 시작",
            )
        elif is_status_ongoing_to_haltafter(from_status, to_status):
            # 운영중(o1) -> 진행중지(s2)

            approval_no = self.get_campaign_approval_no(campaign_id, db)
            # 발송 5분 전부터 취소 불가능
            query = db.query(SendReservationEntity.set_group_msg_seq).filter(
                SendReservationEntity.campaign_id == campaign_id,
                SendReservationEntity.test_send_yn == "n",
            )

            # 5분 전에는 발송 취소 불가
            cancel_allowed_check_cond = [
                SendReservationEntity.send_resv_date > current_korea_timestamp,
                SendReservationEntity.send_resv_date <= current_korea_timestamp_plus_5_minutes,
                SendReservationEntity.send_resv_state == "00",  # 발송요청
            ]
            cancel_allowed_check = query.filter(*cancel_allowed_check_cond)
            if cancel_allowed_check.count() > 0:
                raise PolicyException(
                    detail={
                        "code": "send_resv/halt/denied/01",
                        "message": "발송 5분 전에는 캠페인을 중지할 수 없습니다.",
                    },
                )

            # 리마인드 메세지가 존재하지 않고, 캠페인 메세지가 발송되었을 경우 진행 중지 불가
            remind_msgs = db.query(SetGroupMessagesEntity).filter(
                SetGroupMessagesEntity.campaign_id == campaign_id,
                SetGroupMessagesEntity.msg_resv_date > current_korea_date,
            )
            if remind_msgs.count() == 0:
                raise PolicyException(
                    detail={
                        "code": "send_resv/halt/denied/03",
                        "message": "남은 메세지가 존재하지 않아 캠페인 진행을 중지할 수 없습니다.",
                    },
                )

            # 관련 dag_run 삭제
            await self.delete_dag_run(campaign_id, db, user)

            # 예약 삭제
            delete_statement = delete(SendReservationEntity).where(
                and_(
                    SendReservationEntity.campaign_id == campaign_id,
                    SendReservationEntity.test_send_yn == "n",
                    SendReservationEntity.send_resv_state == "00",
                )
            )
            db.execute(delete_statement)

            # 사용중지로 인한 크레딧 사용 취소
            self.cancel_credit_use(campaign_id, db, user)

        elif is_status_haltbefore_to_pending(from_status, to_status):
            # 일시중지(s1) -> 진행대기(w2)

            approval_no = self.get_campaign_approval_no(campaign_id, db)

            created_at = localtime_converter()
            update_haltbefore_to_pending = (
                update(SendReservationEntity)
                .where(
                    and_(
                        SendReservationEntity.campaign_id == campaign_id,
                        SendReservationEntity.send_resv_state == "21",
                        SendReservationEntity.test_send_yn == "n",
                    )
                )
                .values(
                    {
                        "send_resv_state": "00",
                        "log_comment": "캠페인 진행대기 상태로 변경되었습니다.",
                        "log_date": created_at,
                        "update_resv_date": created_at,
                    }
                )
            )
            db.execute(update_haltbefore_to_pending)

            # 결제 진행
            remind_list = self.campaign_repository.get_campaign_remind(campaign_id, db)
            remaining_credit = self.credit_repository.get_remain_credit(db)
            campaign_cost = self.campaign_set_repository.get_campaign_cost_by_campaign_id(
                campaign_id, db
            )

            new_credit_history = CreditHistory(
                user_name=user.username,
                description=f"캠페인 집행({campaign_id})",
                status=CreditStatus.USE.value,
                use_amount=campaign_cost,
                remaining_amount=remaining_credit - campaign_cost,
                note=f"캠페인 리마인드 {len(remind_list)}건 포함" if len(remind_list) > 0 else None,
                created_by=str(user.user_id),
                updated_by=str(user.user_id),
            )
            self.credit_repository.add_history(new_credit_history, db)

            # 2. remaining_credit 차감
            self.credit_repository.update_credit(-campaign_cost, db)

        elif is_status_haltbefore_to_tempsave(from_status, to_status):
            # 일시중지(s1) -> 임시저장(r1)
            # campaign_approvals 해당 approval_status를 canceled로 변경

            approval_no = self.cancel_campaign_approval(db, campaign_id)

            # 예약 삭제
            delete_statement = delete(SendReservationEntity).where(
                and_(
                    SendReservationEntity.campaign_id == campaign_id,
                    SendReservationEntity.test_send_yn == "n",
                )
            )
            db.execute(delete_statement)

        elif is_status_haltafter_to_modify(from_status, to_status):
            # --진행중지->수정 단계 ("r2")
            approval_no = self.get_campaign_approval_no(campaign_id, db)

        elif is_status_modify_to_haltafter(from_status, to_status):
            # --수정 단계->진행중지 ("s2")
            # send_reservation을 업데이트하고 새로 인서트한다.
            approval_no = self.get_campaign_approval_no(campaign_id, db)

            modify_resv_sync = ModifyReservSync(db, str(user.user_id), campaign_id)
            current_korea_date = datetime.now(selected_timezone).strftime("%Y%m%d")

            result = modify_resv_sync.get_reserve_msgs(current_korea_date)

            if isinstance(result, dict):
                print(result)
                return approval_no
            else:
                msg_seqs_to_save = result

                # insert to send_reservation : 이미 예약한 메세지를 제외하고 예약하기
                res = self.save_campaign_reservation(db, user, campaign_id, msg_seqs_to_save)

                if res:
                    return approval_no
                else:
                    txt = f"{campaign_id} : 당일({current_korea_date}) 정상 예약 메세지가 존재하지 않습니다."
                    print(txt)

        # --진행중지 -> 운영 ("21" 상태의 row 예약 상태 변경 "00")
        elif is_status_haltafter_to_ongoing(from_status, to_status):

            approval_no = self.get_campaign_approval_no(campaign_id, db)

            send_msg_types = (
                db.query(SendReservationEntity.msg_category)
                .filter(
                    SendReservationEntity.campaign_id == campaign_id,
                    SendReservationEntity.test_send_yn == "n",
                    SendReservationEntity.send_resv_state == "00",
                )
                .first()
            )

            if not send_msg_types:
                res = self.save_campaign_reservation(db, user, campaign_id)
                if res is False:
                    raise HTTPException(
                        status_code=400,
                        detail={
                            "code": "send_resv/insert/fail",
                            "message": f"당일({current_korea_date}) 정상 예약 메세지가 존재하지 않습니다.",
                        },
                    )

            # 크레딧 사용 취소 로직 추가
            # 1. 본 캠페인 조회
            campaign = self.campaign_repository.get_campaign_detail(campaign_id, user, db)
            time_to_send = campaign.timetosend

            # 2. 발송당 캠페인 비용 계산
            campaign_reminds = self.campaign_repository.get_campaign_remind(campaign_id, db)

            # 3. 잔여 발송 캠페인(리마인드) 수 확인
            unsent_remind_count = 0
            charge_remind_cost = 0
            for campaign_remind in campaign_reminds:
                # 한국 시간 현재 시간
                kst = timezone(timedelta(hours=9))
                current_time_kst = datetime.now(tz=kst)

                # 리마인드 발송 예약 시간
                remind_date_with_time = datetime.strptime(
                    f"{campaign_remind.remind_date} {time_to_send}", "%Y%m%d %H:%M"
                )
                remind_date_with_time = remind_date_with_time.replace(tzinfo=kst)

                print("remind_date_with_time")
                print(remind_date_with_time)

                print("current_time_kst")
                print(current_time_kst)

                # 리마인드 발송 시간이 아직 도래하지 않음. 해당 리마인드는 결제 필요
                if current_time_kst < remind_date_with_time:
                    unsent_remind_count += 1
                    # 1. campaign_sets를 조회한다.(복수개 가능)
                    campaign_sets = self.campaign_set_repository.get_campaign_set_by_campaign_id(
                        campaign_id, db
                    )
                    for campaign_set in campaign_sets:
                        # 2. campaign_set_groups를 조회한다.(복수개 가능) -> recipient_count
                        campaign_set_groups = campaign_set.set_group_list
                        for campaign_set_group in campaign_set_groups:
                            set_group_messages = self.campaign_set_repository.get_campaign_set_group_messages_by_set_group_seq(
                                campaign_set_group.set_group_seq, db
                            )
                            for set_group_message in set_group_messages:
                                # 3. set_group_message에서 set_group_seq와 remind_step으로 메시지를 찾는다. -> msg_type
                                if set_group_message.remind_step == campaign_remind.remind_step:
                                    msg_type = set_group_message.msg_type
                                    recipient_count = campaign_set_group.recipient_count

                                    # 4. delivery_cost_by_vender에서 발송 금액을 조회하고 recipient_count를 곱한다.
                                    cost_per_send = (
                                        self.campaign_set_repository.get_delivery_cost_by_msg_type(
                                            msg_type, db
                                        )
                                    )
                                    cost_per_set_group = cost_per_send * recipient_count

                                    # 5. charge_remind_cost 계산된 값을 더한다.
                                    charge_remind_cost += cost_per_set_group

            # 5. 결제 진행
            if charge_remind_cost > 0:
                remaining_credit = self.credit_repository.get_remain_credit(db)
                new_credit_history = CreditHistory(
                    user_name=user.username,
                    description=f"캠페인 집행({campaign_id})",
                    status=CreditStatus.USE.value,
                    use_amount=charge_remind_cost,
                    remaining_amount=remaining_credit - charge_remind_cost,
                    note=f"캠페인 리마인드 {unsent_remind_count}건 결제",
                    created_by=str(user.user_id),
                    updated_by=str(user.user_id),
                )
                self.credit_repository.add_history(new_credit_history, db)
                self.credit_repository.update_credit(-charge_remind_cost, db)

        # 진행중지, 운영중 -> 완료, 기간만료 **campaign-dag**
        elif is_status_to_complete_or_expired(from_status, to_status):

            approval_no = self.get_campaign_approval_no(campaign_id, db)

            # ongoing → complete: 완료
            # haltbefore, haltafter → expired : 기간 만료
            created_at = localtime_converter()
            self.save_campaign_logs(
                db=db,
                campaign_id=campaign_id,
                timeline_type="campaign_event",
                created_at=created_at,
                created_by=str(user.user_id),
                created_by_name=user.username,
                description="캠페인 종료",
            )
        else:
            raise PolicyException(detail={"message": "캠페인 상태가 유효하지 않습니다."})

        return approval_no

    def cancel_credit_use(self, campaign_id, db, user):
        # 크레딧 사용 취소 로직 추가
        # 1. 해당 캠페인 비용 확인 -> 본 캠페인 + 리마인드만큼 결제
        campaign_cost = self.campaign_set_repository.get_campaign_cost_by_campaign_id(
            campaign_id, db
        )

        # 2. 리마인드 캠페인 확인
        campaign_reminds = self.campaign_repository.get_campaign_remind(campaign_id, db)
        remind_count = len(campaign_reminds)
        all_campaign_count = remind_count + 1

        # 3. 발송처리된 캠페인 확인
        already_sent_campaigns = self.campaign_repository.get_already_sent_campaigns(
            campaign_id, db
        )
        # 4. 발송 처리되지 않은 부분 조회
        all_remind_step = [campaign_remind.remind_step for campaign_remind in campaign_reminds]
        already_sent_remind_step = [
            already_sent_campaign.remind_step for already_sent_campaign in already_sent_campaigns
        ]

        # 5. 잔여 발송 캠페인(리마인드) 확인
        unsent_remind_steps = list(set(all_remind_step) - set(already_sent_remind_step))

        # 6. 사용취소 금액 계산
        refund_cost = 0
        for remind_step in unsent_remind_steps:
            # 1. campaign_sets를 조회한다.(복수개 가능)
            campaign_sets = self.campaign_set_repository.get_campaign_set_by_campaign_id(
                campaign_id, db
            )
            for campaign_set in campaign_sets:
                # 2. campaign_set_groups를 조회한다.(복수개 가능) -> recipient_count
                campaign_set_groups = campaign_set.set_group_list
                for campaign_set_group in campaign_set_groups:
                    set_group_messages = self.campaign_set_repository.get_campaign_set_group_messages_by_set_group_seq(
                        campaign_set_group.set_group_seq, db
                    )
                    for set_group_message in set_group_messages:
                        # 3. set_group_message에서 set_group_seq와 remind_step으로 메시지를 찾는다. -> msg_type
                        if set_group_message.remind_step == remind_step:
                            msg_type = set_group_message.msg_type
                            recipient_count = campaign_set_group.recipient_count

                            # 4. delivery_cost_by_vender에서 발송 금액을 조회하고 recipient_count를 곱한다.
                            cost_per_send = (
                                self.campaign_set_repository.get_delivery_cost_by_msg_type(
                                    msg_type, db
                                )
                            )
                            cost_per_set_group = cost_per_send * recipient_count

                            # 5. charge_remind_cost 계산된 값을 더한다.
                            refund_cost += cost_per_set_group

        # 크레딧 이력 테이블 저장
        remaining_amount = self.credit_repository.get_remain_credit(db)
        refund_credit_history = CreditHistory(
            user_name=user.username,
            description=f"캠페인({campaign_id}) 중지로 인한 크레딧 사용 취소",
            status=CreditStatus.REFUND.value,
            charge_amount=refund_cost,
            remaining_amount=remaining_amount + refund_cost,
            created_by=str(user.user_id),
            updated_by=str(user.user_id),
        )
        self.credit_repository.add_history(refund_credit_history, db)

        # 3. 잔여 크레딧 테이블에 사용취소 크레딧 합산
        self.credit_repository.update_credit(refund_cost, db)

    async def delete_dag_run(self, campaign_id, db, user):
        # 1. send_dag_log -> dag_run_id 조회
        # 2. 해당 dag_run_id 삭제 요청
        send_reservation_entity = (
            db.query(SendReservationEntity)
            .filter(SendReservationEntity.campaign_id == campaign_id)
            .first()
        )
        send_dag_log = (
            db.query(SendDagLogEntity)
            .filter(
                SendDagLogEntity.campaign_id == campaign_id,
                SendDagLogEntity.send_resv_date == send_reservation_entity.send_resv_date,
            )
            .first()
        )
        try:
            await self.message_controller.delete_dag_run(
                dag_name=f"{user.mall_id}_issue_coupon", dag_run_id=send_dag_log.dag_run_id
            )

            await self.message_controller.delete_dag_run(
                dag_name=f"{user.mall_id}_send_messages", dag_run_id=send_dag_log.dag_run_id
            )
        except HTTPException as e:
            print(f"이미 삭제된 dag_run 입니다.: {send_dag_log.dag_run_id}")

    def get_campaign_approval_no(self, campaign_id, db):
        approval_status = CampaignApprovalStatus.APPROVED.value
        approval_obj = self.get_campaign_approval_obj(db, campaign_id, approval_status)
        if not approval_obj:
            raise NotFoundException(detail={"message": "승인 정보를 찾지 못했습니다."})
        approval_no = approval_obj.approval_no
        return approval_no

    async def today_approval_campaign_execute(
        self,
        db,
        from_status,
        to_status,  # o1
        campaign_id,
        created_at,
        created_by,
        created_by_name,
        user,
        send_date,
        send_time,
        approval_no=None,
    ):

        # 상태 변경 로그 -> 운영중
        ongoing_status_hist = CampaignStatusHistoryEntity(
            campaign_id=campaign_id,
            from_status=from_status,
            to_status=to_status,
            created_at=created_at,
            approval_no=approval_no,  # if approval_no 초기값은 None
            created_by=created_by,
        )

        db.add(ongoing_status_hist)
        db.flush()

        status_no = ongoing_status_hist.status_no

        # 캠페인 타임라인 로그 저장(1) - 캠페인 시작
        self.save_campaign_logs(
            db=db,
            campaign_id=campaign_id,
            timeline_type="campaign_event",
            created_at=created_at,
            created_by=created_by,
            created_by_name=created_by_name,
            description="캠페인 시작",
        )

        # 캠페인 타임라인 로그 저장(2) - 운영중
        self.save_campaign_logs(
            db=db,
            campaign_id=campaign_id,
            timeline_type=CampaignTimelineType.STATUS_CHANGE.value,
            created_at=created_at,
            created_by=created_by,
            created_by_name=created_by_name,
            to_status=to_status,
            status_no=status_no,
        )

        # insert to send_reservation
        res = self.save_campaign_reservation(db, user, campaign_id)

        if res:
            # airflow trigger api
            print("today airflow trigger api")
            input_var = {
                "mallid": user.mall_id,
                "campaign_id": campaign_id,
                "test_send_yn": "n",
            }
            yyyymmddhh24mi = get_korean_current_datetime_yyyymmddhh24mims()
            unix_timestamp_now = get_unix_timestamp()
            dag_run_id = f"{campaign_id}_{str(yyyymmddhh24mi)}_{str(unix_timestamp_now)}"
            logical_date = create_logical_date_for_airflow(send_date, send_time)

            # await self.message_controller.execute_dag(
            #     dag_name=f"{user.mall_id}_send_messages",
            #     input_vars=input_var,
            #     dag_run_id=dag_run_id,
            #     logical_date=logical_date,
            # )

            send_reservation_entity = (
                db.query(SendReservationEntity)
                .filter(SendReservationEntity.campaign_id == campaign_id)
                .first()
            )
            send_dag_log_entity = SendDagLogEntity(
                campaign_id=campaign_id,
                send_resv_date=send_reservation_entity.send_resv_date,
                dag_run_id=dag_run_id,
            )
            db.add(send_dag_log_entity)
            db.flush()

            await self.message_controller.execute_dag(
                dag_name=f"{user.mall_id}_issue_coupon",
                input_vars=input_var,
                dag_run_id=dag_run_id,
                logical_date=logical_date,
            )

        else:
            return False

        return True

    def cancel_campaign_approval(self, db: Session, campaign_id: str):

        approval_obj = (
            db.query(CampaignApprovalEntity)
            .filter(
                CampaignApprovalEntity.campaign_id == campaign_id,
                CampaignApprovalEntity.approval_status == CampaignApprovalStatus.APPROVED.value,
            )
            .first()
        )

        if not approval_obj:
            raise NotFoundException(detail={"message": "승인 정보를 찾지 못했습니다."})

        approval_obj.approval_status = CampaignApprovalStatus.CANCELED.value

        return approval_obj.approval_no

    def save_campaign_reservation(self, db, user_obj, campaign_id, msg_seqs_to_save=None):
        """
        - msg_update_thres: 메세지 예약 발송일자 변경 기준일자

        - (메세지 발송예약일자 == 당일) 인 메세지만 저장

        -- 수정 시 test_send_executions_v2 api 영향도 체크 필요
        -- to-do : 처음 생성된 정보 <-> (수정단계 -> 진행중지)수정할 때 join 정보 불일치 영향도 고려
        """

        try:
            # logging
            tz = "Asia/Seoul"
            korea_timezone = pytz.timezone(tz)
            curren_time = datetime.now(korea_timezone)
            current_date = curren_time.strftime("%Y%m%d")

            log_file_path = f"./logs/send_reserv_log_{current_date}.logs"

            logging.basicConfig(
                filename=log_file_path,
                level=logging.INFO,
                format="%(asctime)s - %(levelname)s - %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S",
                encoding="utf-8",
            )

            logging.info(f"1 .campaign_id: {campaign_id} 예약일({current_date})")

            offer_detail = (
                db.query(
                    OffersEntity.coupon_no,
                    func.min(
                        coalesce(OffersEntity.benefit_price, OffersEntity.benefit_percentage)
                    ).label("offer_amount"),
                )
                .group_by(OffersEntity.coupon_no)
                .subquery()
            )

            # messages
            set_group_message = (
                db.query(
                    CampaignEntity.campaign_group_id,
                    CampaignEntity.campaign_id,  # 캠페인 아이디
                    CampaignEntity.campaign_name,
                    CampaignEntity.shop_send_yn,  # shop_send_yn
                    func.to_char(
                        func.to_date(CampaignEntity.start_date, "YYYYMMDD"), "YYYY-MM-DD"
                    ).label("start_date"),
                    # 캠페인 시작일
                    func.to_char(
                        func.to_date(CampaignEntity.end_date, "YYYYMMDD"), "YYYY-MM-DD"
                    ).label("end_date"),
                    # 캠페인 종료일
                    CampaignEntity.msg_delivery_vendor,
                    CampaignEntity.timetosend,
                    CampaignSetsEntity.audience_id,
                    CampaignSetsEntity.coupon_no,
                    SetGroupMessagesEntity.set_group_msg_seq,
                    CampaignSetGroupsEntity.set_sort_num,
                    CampaignSetGroupsEntity.group_sort_num,
                    OffersEntity.coupon_no,  # 오퍼 아이디
                    offer_detail.c.offer_amount,  # 오퍼 amount
                    func.to_char(
                        func.to_date(OffersEntity.available_begin_datetime, "YYYYMMDD"),
                        "YYYY-MM-DD",
                    ).label(
                        "event_str_dt"
                    ),  # 오퍼 시작일
                    func.to_char(
                        func.to_date(OffersEntity.available_end_datetime, "YYYYMMDD"), "YYYY-MM-DD"
                    ).label(
                        "event_end_dt"
                    ),  # 오퍼 종료일
                    SetGroupMessagesEntity.media,
                    SetGroupMessagesEntity.msg_type,
                    SetGroupMessagesEntity.msg_send_type,
                    SetGroupMessagesEntity.msg_title,
                    SetGroupMessagesEntity.msg_body,
                    SetGroupMessagesEntity.msg_gen_key,
                    SetGroupMessagesEntity.msg_photo_uri,
                    SetGroupMessagesEntity.msg_announcement,
                    SetGroupMessagesEntity.phone_callback,
                    SetGroupMessagesEntity.bottom_text,
                    SetGroupMessagesEntity.msg_resv_date,  # 예약 발송 날짜
                    SetGroupMessagesEntity.template_id,
                    MessageTemplateEntity.template_key,  # 템플릿 키
                    SetGroupMessagesEntity.remind_seq,
                    SetGroupMessagesEntity.remind_step,
                    SetGroupMessagesEntity.is_used,
                )
                .join(
                    CampaignSetsEntity, CampaignEntity.campaign_id == CampaignSetsEntity.campaign_id
                )
                .join(
                    CampaignSetGroupsEntity,
                    CampaignSetsEntity.set_seq == CampaignSetGroupsEntity.set_seq,
                )
                .join(
                    SetGroupMessagesEntity,
                    CampaignSetGroupsEntity.set_group_seq == SetGroupMessagesEntity.set_group_seq,
                )
                .outerjoin(
                    MessageTemplateEntity,
                    SetGroupMessagesEntity.template_id == MessageTemplateEntity.template_id,
                )
                .outerjoin(OffersEntity, CampaignSetsEntity.coupon_no == OffersEntity.coupon_no)
                .outerjoin(offer_detail, OffersEntity.coupon_no == offer_detail.c.coupon_no)
                .filter(
                    CampaignSetsEntity.campaign_id == campaign_id,
                    SetGroupMessagesEntity.is_used == True,  # 사용 설정된 메세지만 필터링
                )
            )

            # 중복제거
            cus_info_all = db.query(
                CustomerMasterEntity.cus_cd,
                CustomerMasterEntity.hp_no,
                CustomerMasterEntity.track_id,
            ).distinct(
                CustomerMasterEntity.cus_cd,
                CustomerMasterEntity.hp_no,
                CustomerMasterEntity.track_id,
            )

            # TODO [테스트 고객]이 고객마스터에 있는지 확인
            test_cus = ["0005615876", "0005620054", "0005620055"]
            test_cus_arr = cus_info_all.filter(CustomerMasterEntity.cus_cd.in_(test_cus)).all()
            test_cus_cd_lst = [(item[0], item[1]) for item in test_cus_arr]

            logging.info(f"2. 테스트 고객: {str(test_cus_cd_lst)}")
            set_group_message_df = DataConverter.convert_query_to_df(set_group_message)
            logging.info(set_group_message_df)
            set_group_messages_seqs = list(set(set_group_message_df["set_group_msg_seq"]))
            set_group_messages_seqs_str = [str(item) for item in set_group_messages_seqs]

            logging.info(
                f'3. campaign set_group_messages_seqs: {",".join(set_group_messages_seqs_str)}'
            )
            if msg_seqs_to_save:
                msg_seqs_to_save_str = [str(item) for item in msg_seqs_to_save]
            else:
                msg_seqs_to_save_str = []

            logging.info(f'4. 발송 지정 메세지: {",".join(msg_seqs_to_save_str)}')

            cus_info = cus_info_all.subquery()
            subquery = set_group_message.subquery()

            # recipients & messages
            rsv_msg_filter = [
                subquery.c.msg_body.isnot(None),  # 메세지 본문이 Null인 메세지 제외
                subquery.c.msg_body != "",  # 메세지 본문이 공백인 메세지 제외
                subquery.c.msg_resv_date
                == current_date,  # 당일에 발송되어야하는 메세지 예약 저장하기
            ]

            send_rsv_query_1 = (
                db.query(
                    CampaignSetRecipientsEntity.campaign_id,
                    CampaignSetRecipientsEntity.set_sort_num,
                    CampaignSetRecipientsEntity.group_sort_num,
                    CampaignSetRecipientsEntity.cus_cd,  # cus_cd
                    CampaignSetRecipientsEntity.contents_id,
                    CampaignSetRecipientsEntity.rep_nm,
                    ContentsEntity.contents_name,
                    ContentsEntity.contents_url,
                    subquery.c.shop_send_yn,  # shop_send_yn
                    subquery.c.set_group_msg_seq,
                    subquery.c.campaign_name,
                    subquery.c.audience_id,
                    subquery.c.coupon_no,
                    subquery.c.start_date.label("campaign_start_date"),
                    subquery.c.end_date.label("campaign_end_date"),
                    subquery.c.offer_amount.label("offer_amount"),
                    subquery.c.event_str_dt.label("offer_start_date"),
                    subquery.c.event_end_dt.label("offer_end_date"),
                    subquery.c.msg_resv_date.label("send_resv_date"),  # -> to-do: timestamptz
                    subquery.c.timetosend,  # -> to-do: timestamptz
                    cus_info.c.hp_no.label("phone_send"),
                    cus_info.c.track_id,  # track_id
                    subquery.c.msg_delivery_vendor.label("send_sv_type"),
                    subquery.c.msg_type.label("send_msg_type"),  # sms, lms, kakao_image_wide, ..
                    subquery.c.msg_send_type.label("msg_category"),  # campaign, remind
                    subquery.c.remind_step,  # remind_step
                    subquery.c.msg_title.label("send_msg_subject"),
                    subquery.c.msg_body.label("send_msg_body"),
                    subquery.c.bottom_text,
                    subquery.c.phone_callback,
                    subquery.c.msg_announcement,
                    subquery.c.template_key.label("kko_template_key"),
                )
                .join(
                    subquery,
                    (CampaignSetRecipientsEntity.campaign_id == subquery.c.campaign_id)
                    & (CampaignSetRecipientsEntity.set_sort_num == subquery.c.set_sort_num)
                    & (CampaignSetRecipientsEntity.group_sort_num == subquery.c.group_sort_num),
                )
                .outerjoin(cus_info, CampaignSetRecipientsEntity.cus_cd == cus_info.c.cus_cd)
                .outerjoin(
                    ContentsEntity,
                    CampaignSetRecipientsEntity.contents_id == ContentsEntity.contents_id,
                )
                .filter(and_(*rsv_msg_filter))
            )
            send_rsv_1 = DataConverter.convert_query_to_df(send_rsv_query_1)
            initial_rsv_1_count = len(send_rsv_1)
            logging.info(f"5. 당일 발송 수: {initial_rsv_1_count}")

            # left join 고객마스터에 존재하는(휴대폰 번호가 존재하는) 고객만 필터하기
            rsv_msg_filter_2 = [cus_info.c.hp_no.isnot(None), cus_info.c.hp_no != ""]

            # 지정된 메세지만 발송예약하기
            if msg_seqs_to_save:
                # msg_seqs_to_save: list
                rsv_msg_filter_2.append(subquery.c.set_group_msg_seq.in_(msg_seqs_to_save))

            send_rsv_query = send_rsv_query_1.filter(and_(*rsv_msg_filter_2))
            send_rsv = DataConverter.convert_query_to_df(send_rsv_query)

            initial_rsv_count = len(send_rsv)
            logging.info(f"6. 당일 발송 수(고객마스터에 존재하는 고객만 필터): {initial_rsv_count}")

            if initial_rsv_count == 0:
                logging.info("7. 오늘 발송되는 메세지가 존재하지 않습니다")
                return False

            # kko_button_json
            set_group_msg_seqs = [
                row._asdict()["set_group_msg_seq"] for row in set_group_message.all()
            ]

            # contents_url 개인화 코드
            send_rsv_format = send_rsv[  # pyright: ignore [reportAssignmentType]
                [
                    "campaign_id",
                    "set_sort_num",
                    "group_sort_num",
                    "cus_cd",
                    "set_group_msg_seq",
                    "contents_name",
                    "contents_url",
                    "track_id",
                ]
            ]
            try:
                button_df_convert = convert_to_button_format(
                    db, set_group_msg_seqs, send_rsv_format
                )
            except Exception as e:
                raise Exception(e)

            logging.info("8. button 개인화 적용 전 row수 :" + str(len(send_rsv_format)))
            group_keys = [
                "campaign_id",
                "set_sort_num",
                "group_sort_num",
                "cus_cd",
                "set_group_msg_seq",
            ]
            send_rsv_format = send_rsv_format.merge(button_df_convert, on=group_keys, how="left")
            del send_rsv_format["contents_name"]
            del send_rsv_format["contents_url"]

            notnullbtn = send_rsv_format[send_rsv_format["kko_button_json"].notnull()]
            isnullbtn = send_rsv_format[send_rsv_format["kko_button_json"].isnull()]
            notnullbtn = notnullbtn[
                ~notnullbtn["kko_button_json"].str.contains("{{")
            ]  # 포매팅이 안되어 있는 메세지는 제외한다.
            send_rsv_format = pd.concat(  # pyright: ignore [reportCallIssue]
                [notnullbtn, isnullbtn]  # pyright: ignore [reportArgumentType]
            )
            logging.info("9. button 개인화 적용 후 row수 :" + str(len(send_rsv_format)))

            send_rsv_format = send_rsv.merge(send_rsv_format, on=group_keys, how="left")

            # set_group_msg_seq : send_filepath, send_filecount
            union_query = get_message_resources(db, set_group_msg_seqs)
            resource_df = DataConverter.convert_query_to_df(union_query)
            resource_df["send_filepath"] = resource_df["send_filepath"].apply(
                lambda lst: ";".join(lst)
            )

            send_rsv_format: pd.DataFrame = send_rsv_format.merge(
                resource_df, on="set_group_msg_seq", how="left"
            )

            # 파일이 없는 경우 nan -> 0
            send_rsv_format["send_filecount"] = send_rsv_format["send_filecount"].fillna(0)

            # 개인화변수 formatting (발송번호)
            # contents_name
            logging.info("10. send_msg_body 개인화 적용 전 row수 :" + str(len(send_rsv_format)))

            personal_processing = send_rsv_format[
                [
                    "set_group_msg_seq",
                    "cus_cd",
                    "rep_nm",
                    "contents_url",
                    "contents_name",
                    "campaign_start_date",
                    "campaign_end_date",
                    "offer_start_date",
                    "offer_end_date",
                    "offer_amount",
                    "send_msg_body",
                    "phone_callback",
                ]
            ]

            personal_processing_fm = personal_variable_formatting(
                db, personal_processing  # pyright: ignore [reportArgumentType]
            )  # pyright: ignore [reportArgumentType]

            personal_processing_fm = personal_processing_fm[  # pyright: ignore [reportCallIssue]
                ["set_group_msg_seq", "cus_cd", "send_msg_body", "phone_callback"]
            ].rename(
                columns={"send_msg_body": "send_msg_body_fm", "phone_callback": "phone_callback_fm"}
            )

            send_rsv_format = send_rsv_format.merge(
                personal_processing_fm, on=["set_group_msg_seq", "cus_cd"], how="left"
            )

            del send_rsv_format["send_msg_body"]
            del send_rsv_format["phone_callback"]

            send_rsv_format.rename(
                columns={
                    "send_msg_body_fm": "send_msg_body",
                    "phone_callback_fm": "phone_callback",
                },
                inplace=True,
            )

            send_rsv_format = send_rsv_format[  # pyright: ignore [reportAssignmentType]
                ~send_rsv_format["send_msg_body"].str.contains("{{")
            ]  # 포매팅이 안되어 있는 메세지는 제외한다.

            send_rsv_format = send_rsv_format[  # pyright: ignore [reportAssignmentType]
                ~send_rsv_format["phone_callback"].str.contains("{{")
            ]  # 포매팅이 안되어 있는 메세지는 제외한다.

            logging.info("11. send_msg_body 개인화 적용 후 row수 :" + str(len(send_rsv_format)))

            # 발송사, 메세지 타입에 따른 기타 변수 생성
            ##카카오발신프로필, 카카오템플릿키, 카카오친구톡광고표시, 카카오친구톡와이드이미지사용, 카카오알림톡 유형
            ##SSG 재발송 시도 여부, kko_send_timeout, kakao_send_profile_key
            send_rsv_format = convert_by_message_format(  # pyright: ignore [reportAssignmentType]
                send_rsv_format
            )  # pyright: ignore [reportAssignmentType]

            # 고객 중복 여부 체크
            keys = ["campaign_id", "remind_step", "cus_cd"]
            is_duplicate = send_rsv_format.duplicated(subset=keys, keep=False)

            if sum(is_duplicate) > 0:
                raise DuplicatedException(
                    detail={
                        "code": "send_reservation/duplicated",
                        "message": "중복된 고객이 존재합니다.",
                    },
                )

            # 일괄적용
            # 고정값 None (send_resv_state, send_rstl_state, kko_at_accent, kko_at_price, kko_at_currency, kko_ft_subject, kko_at_item_json)
            send_rsv_format["send_resv_state"] = None
            send_rsv_format["send_rslt_state"] = None
            send_rsv_format["kko_at_accent"] = None
            send_rsv_format["kko_at_price"] = None
            send_rsv_format["kko_at_currency"] = None
            send_rsv_format["kko_ft_subject"] = None
            send_rsv_format["kko_at_item_json"] = None
            send_rsv_format["send_rstl_seq"] = None

            # 고정값
            send_rsv_format["test_send_yn"] = "n"
            send_rsv_format["kko_ssg_retry"] = 0  # 재발송 시도 횟수
            send_rsv_format["sent_success"] = "n"

            # 발송요청날짜
            send_rsv_format["send_resv_date"] = pd.to_datetime(
                send_rsv_format["send_resv_date"] + " " + send_rsv_format["timetosend"],
                format="%Y%m%d %H:%M",
            )

            curr_date = localtime_converter()
            send_rsv_format["send_rslt_date"] = curr_date
            send_rsv_format["create_resv_date"] = curr_date
            send_rsv_format["create_resv_user"] = user_obj.user_id
            send_rsv_format["update_resv_date"] = curr_date
            send_rsv_format["update_resv_user"] = user_obj.user_id

            # 저장
            send_reserv_columns = [
                column.name
                for column in SendReservationEntity.__table__.columns
                if column.name
                not in ["send_resv_seq", "shop_cd", "coupon_no", "log_date", "log_comment"]
            ]

            res_df = send_rsv_format[send_reserv_columns]

            final_rsv = len(res_df)
            if final_rsv == 0:
                logging.info("12. 오늘 발송되는 정상 메세지가 존재하지 않습니다")
                return False

            res_df = res_df.replace({np.nan: None})
            res_df["phone_callback"] = res_df["phone_callback"].str.replace("-", "")
            res_df["phone_send"] = res_df["phone_send"].str.replace("-", "")

            # kko_button_json이 null인 경우, {"button": []} 를 넣어줘야 함, 그리고 리스트 형태로 만들어야 함
            res_df["kko_button_json"] = res_df["kko_button_json"].fillna('{"button": []}')

            res_df["remind_step"] = res_df["remind_step"].fillna(0)

            send_rsv_dict = res_df.to_dict("records")  # pyright: ignore [reportArgumentType]
            db.bulk_insert_mappings(SendReservationEntity, send_rsv_dict)

            remind_step = int(res_df["remind_step"].fillna(0).iloc[0])

            self.save_campaign_logs(
                db=db,
                campaign_id=campaign_id,
                timeline_type=CampaignTimelineType.SEND_REQUEST.value,
                created_at=curr_date,
                created_by=user_obj.user_id,
                created_by_name=user_obj.username,
                description=f"{initial_rsv_count:,}건 중 {final_rsv:,}건 발송 요청 예약",  # to-do: campagin/remind 발송 구분
                remind_step=remind_step,
            )

            db.flush()

            return True

        except Exception as e:
            db.rollback()
            print(e)
            raise ConsistencyException(detail={"message": "승인 완료 처리 중 문제가 발생했습니다."})
