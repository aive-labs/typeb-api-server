from datetime import datetime, timedelta

import pytz
from sqlalchemy import delete, desc
from sqlalchemy.orm import Session
from starlette.background import BackgroundTasks

from src.campaign.enums.campagin_status import CampaignStatus
from src.campaign.enums.campaign_approval_status import CampaignApprovalStatus
from src.campaign.enums.campaign_timeline_type import CampaignTimelineType
from src.campaign.infra.entity.approver_entity import ApproverEntity
from src.campaign.infra.entity.campaign_approval_entity import CampaignApprovalEntity
from src.campaign.infra.entity.campaign_entity import CampaignEntity
from src.campaign.infra.entity.campaign_status_history_entity import (
    CampaignStatusHistoryEntity,
)
from src.campaign.infra.entity.campaign_timeline_entity import CampaignTimelineEntity
from src.campaign.infra.entity.coupon_custs import OfferCustEntity
from src.campaign.infra.entity.send_reservation_entity import SendReservationEntity
from src.campaign.infra.entity.set_group_messages_entity import SetGroupMessagesEntity
from src.campaign.infra.sqlalchemy_query.modify_reservation_sync_service import (
    ModifyReservSync,
)
from src.campaign.routes.port.approve_campaign_usecase import ApproveCampaignUseCase
from src.campaign.service.background.save_offer_custs import save_offer_custs
from src.common.sqlalchemy.object_access_condition import object_access_condition
from src.common.timezone_setting import selected_timezone
from src.common.utils.date_utils import localtime_converter
from src.core.exceptions.exceptions import NotFoundException, PolicyException
from src.messages.service.message_reserve_controller import MessageReserveController
from src.users.domain.user import User
from src.users.infra.entity.user_entity import UserEntity


class ApproveCampaignService(ApproveCampaignUseCase):

    def exec(
        self,
        campaign_id,
        to_status,
        db: Session,
        user: User,
        background_task: BackgroundTasks,
        reviewers_str: str | None = None,
    ):
        """
        캠페인 상태 변경 API

        - 캠페인 상태로그 : campaign_status_history
        - 리뷰 요청
            - 캠페인 승인 : campaign_approvals
            - 승인자 : approvers
        - 캠페인 타임라인 인서트 : campaign_timeline

        - campaign-dag : to_status (o1 운영중, o2 완료, s3 기간만료)
        """
        user_obj = user
        created_at = localtime_converter()
        datetime_obj = datetime.fromisoformat(created_at)
        today = datetime_obj.strftime("%Y%m%d")

        condition = object_access_condition(db, user_obj, CampaignEntity)
        campaign_obj = (
            db.query(CampaignEntity)
            .filter(CampaignEntity.campaign_id == campaign_id, *condition)
            .first()
        )
        if not campaign_obj:
            raise PolicyException(
                detail={
                    "code": "campaign/status/denied/access",
                    "message": "상태 변경 권한이 존재하지 않습니다.",
                },
            )

        # 변경전 캠페인 상태
        from_status = campaign_obj.campaign_status_code
        send_date = (
            campaign_obj.send_date if campaign_obj.send_date else campaign_obj.start_date
        )  # 주기성

        # 초기값
        approval_no = None
        status_no = None
        approval_time_log_skip = False
        approval_excute = False

        # 승인 요청
        if (from_status == CampaignStatus.tempsave.value) and (
            to_status == CampaignStatus.review.value
        ):

            if today > send_date:
                raise PolicyException(
                    detail={
                        "code": "campaign/status/denied/access",
                        "message": "발송일자는 승인일 이후만 가능합니다. 발송일자를 변경해주세요. (현재 메시지 발송일자: {send_date})",
                    },
                )

            # 캠페인 승인 테이블 저장
            new_approver = CampaignApprovalEntity(
                campaign_id=campaign_id,
                requester=user_obj.user_id,
                approval_status=CampaignApprovalStatus.REVIEW.value,  # 이 예시에서는 상태를 'REVIEW'로 가정
                created_at=created_at,
                created_by=user_obj.user_id,
                updated_at=created_at,  # 생성 시점에 updated_at도 설정
                updated_by=user_obj.user_id,
            )
            db.add(new_approver)

            # 캠페인 승인번호
            db.flush()
            approval_no = new_approver.approval_no

            # 캠페인 승인자 테이블 저장
            if reviewers_str:
                reviewer_ids = [int(user_id) for user_id in reviewers_str.split(",")]
            else:
                reviewer_ids = []

            reviewers = db.query(UserEntity).filter(UserEntity.user_id.in_(reviewer_ids)).all()

            for user in reviewers:
                approvers = ApproverEntity(
                    campaign_id=campaign_id,
                    approval_no=approval_no,
                    user_id=user.user_id,
                    user_name=user.username,
                    department_id=user.department_id,
                    department_name=user.department_name,
                    department_abb_name=user.department_abb_name,
                    is_approved=False,  # 기초값 False
                    created_at=created_at,
                    created_by=user_obj.user_id,
                    updated_at=created_at,
                    updated_by=user_obj.user_id,
                )

                db.add(approvers)

        # 승인 거절: 승인자 중 한명이라도 거절했을 경우, 해당 승인 건은 무효. 캠페인 상태는 임시저장 상태로 변경
        elif (from_status == CampaignStatus.review.value) and (
            to_status == CampaignStatus.tempsave.value
        ):

            # 현재 승인거절이 가능한 유효힌 approval_no의 reviewer 가져오기
            approvers = self.get_campaign_approvers_to_review(db, campaign_id)
            reviewer_ids = [row._asdict()["user_id"] for row in approvers]

            if user_obj.user_id not in reviewer_ids:
                raise PolicyException(
                    detail={
                        "code": "campaign/approval/denied/01",
                        "message": "승인 권한이 존재하지 않습니다.",
                    },
                )

            # 승인 거절하기

            # 캠페인의 review 상태의 결재 건이 하나만 존재하는 것이 전제되어야함
            approval_status = CampaignApprovalStatus.REVIEW.value
            approval_obj = self.get_campaign_approval_obj(db, campaign_id, approval_status)
            if not approval_obj:
                raise NotFoundException(detail={"message": "승인 정보를 찾지 못했습니다."})
            approval_obj.approval_status = CampaignApprovalStatus.REJECTED.value  # 해당 캠페인 무효
            approval_no = approval_obj.approval_no

            # 승인 거절 : 캠페인 타임라인 로그
            res = self.save_campaign_logs(
                db=db,
                campaign_id=campaign_id,
                timeline_type="approval",
                created_at=created_at,
                created_by=user_obj.user_id,
                created_by_name=user_obj.username,
                to_status=to_status,
                status_no=None,
            )

        # 리뷰중 -> 진행대기 : "승인"
        elif (from_status == CampaignStatus.review.value) and (
            to_status == CampaignStatus.pending.value
        ):

            # 현재 승인이 가능한 유효힌 approval_no의 reviewer 가져오기
            approvers = self.get_campaign_approvers_to_review(db, campaign_id)
            reviewer_ids = [row._asdict()["user_id"] for row in approvers]

            if user_obj.user_id not in reviewer_ids:
                raise PolicyException(
                    detail={
                        "code": "campaign/approval/denied/01",
                        "message": "승인 권한이 존재하지 않습니다.",
                    },
                )

            # 해당 승인 오브젝트 조회
            approval_status = CampaignApprovalStatus.REVIEW.value
            approval_obj = self.get_campaign_approval_obj(db, campaign_id, approval_status)
            if not approval_obj:
                raise NotFoundException(detail={"message": "승인 정보를 찾지 못했습니다."})
            approval_no = approval_obj.approval_no

            if len(reviewer_ids) == 1 and user_obj.user_id == reviewer_ids[0]:
                # 본인을 제외한 다른 리뷰어가 모두 승인했는 경우, 해당 승인 건을 승인 처리하기
                approval_obj.approval_status = CampaignApprovalStatus.APPROVED.value

                # 리뷰어의 승인여부 업데이트하기
                self.approve_campaign_review(db, campaign_id, approval_no, user_obj.user_id)

                # 승인 처리
                res = self.save_campaign_logs(
                    db=db,
                    campaign_id=campaign_id,
                    timeline_type="approval",
                    created_at=created_at,
                    created_by=user_obj.user_id,
                    created_by_name=user_obj.username,
                    to_status=to_status,  # 분기처리에 필요한 값. 타임로그에는 저장 x
                    status_no=None,
                )

                # 캠페인 승인 완료
                approval_excute = True
                res = self.save_campaign_logs(
                    db=db,
                    campaign_id=campaign_id,
                    timeline_type="approval",
                    created_at=created_at,
                    created_by=user_obj.user_id,
                    created_by_name=user_obj.username,
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
                self.approve_campaign_review(db, campaign_id, approval_no, user_obj.user_id)

                # 승인 처리
                res = self.save_campaign_logs(
                    db=db,
                    campaign_id=campaign_id,
                    timeline_type="approval",
                    created_at=created_at,
                    created_by=user_obj.user_id,
                    created_by_name=user_obj.username,
                    to_status=CampaignStatus.pending.value,  # 분기처리에 필요한 값. 타임로그에는 저장 x
                    status_no=None,
                )

        else:
            # 승인 처리 외 상태변경
            approval_no = self.status_general_change(
                db, user_obj, from_status, to_status, campaign_id, background_task
            )

        # 캠페인 상태 변경
        campaign_status = CampaignStatus.get_eums()
        campaign_status_input = [
            (i["_value_"], i["desc"], i["group"], i["group_desc"])
            for i in campaign_status
            if i["_value_"] == to_status
        ][0]

        campaign_obj.campaign_status_code = campaign_status_input[0]
        campaign_obj.campaign_status_name = campaign_status_input[1]
        campaign_obj.campaign_status_group_code = campaign_status_input[2]
        campaign_obj.campaign_status_group_name = campaign_status_input[3]

        status_hist = CampaignStatusHistoryEntity(
            campaign_id=campaign_id,
            from_status=from_status,
            to_status=to_status,
            created_at=created_at,
            approval_no=approval_no,  # if approval_no 초기값은 None
            created_by=user_obj.user_id,
        )

        db.add(status_hist)

        db.flush()
        status_no = status_hist.status_no  # 캠페인 상태 번호

        if approval_time_log_skip:
            # 일부 승인자 승인 후 캠페인 상태가 변경하지 않은 경우, 타임로그에 표시하지 않는다. ex) w1 -> w1
            pass

        else:
            # 캠페인 타임라인 로그 저장
            res = self.save_campaign_logs(
                db=db,
                campaign_id=campaign_id,
                timeline_type=CampaignTimelineType.STATUS_CHANGE.value,
                created_at=created_at,
                created_by=user_obj.user_id,
                created_by_name=user_obj.username,
                to_status=to_status,
                status_no=status_no,
            )

        db.commit()

        # 당일 (승인 -> 발송)
        if (to_status == "w2") and (approval_excute is True) and (send_date == today):

            pending = CampaignStatus.pending.value
            ongoing = CampaignStatus.ongoing.value

            # 캠페인 상태를 "운영중"으로 변경
            campaign_obj = (
                db.query(CampaignEntity).filter(CampaignEntity.campaign_id == campaign_id).first()
            )
            if not campaign_obj:
                raise NotFoundException(detail={"message": "캠페인 정보를 찾지 못했습니다."})
            campaign_obj.campaign_status_code = "o1"
            campaign_obj.campaign_status_name = "운영중"
            campaign_obj.campaign_status_group_code = "o"
            campaign_obj.campaign_status_group_name = "운영단계"

            # 발송 예약
            res = self.today_approval_campaign_excute(
                db,
                from_status=pending,
                to_status=ongoing,
                campaign_id=campaign_id,
                created_at=created_at,
                created_by=user_obj.user_id,
                created_by_name=user_obj.username,
                user_obj=user_obj,
                background_task=background_task,
                approval_no=approval_no,
            )
            if res is False:
                txt = f"{campaign_id} : 당일 발송할 정상 예약 메세지가 존재하지 않습니다."
                return {"result": txt}
            else:
                db.commit()

        return {"res": "success"}

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
    ):

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

        elif timeline_type == CampaignTimelineType.SEND_MSG.value:
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
                ApproverEntity.user_id == user_id,
            )
            .first()
        )

        if not approver:
            raise NotFoundException(detail={"message": "승인 정보를 찾지 못했습니다."})

        approver.is_approved = True

    def status_general_change(
        self, db, user_obj, from_status, to_status, campaign_id, background_task
    ):
        # --진행대기 -> 일시중지 (00상태의 row 예약 상태 변경 "21")
        if (from_status == CampaignStatus.pending.value) and (
            to_status == CampaignStatus.haltbefore.value
        ):

            approval_status = CampaignApprovalStatus.APPROVED.value
            approval_obj = self.get_campaign_approval_obj(db, campaign_id, approval_status)
            if not approval_obj:
                raise NotFoundException(detail={"message": "승인 정보를 찾지 못했습니다."})
            approval_no = approval_obj.approval_no

            # to-do: 예약이 이미 되었다면 취소 execute
            query = db.query(SendReservationEntity).filter(
                SendReservationEntity.campaign_id == campaign_id,
                SendReservationEntity.test_send_yn == "n",
            )

            # 발송 취소 로깅
            created_at = localtime_converter()
            res = self.save_campaign_logs(
                db=db,
                campaign_id=campaign_id,
                timeline_type="halt_msg",
                created_at=created_at,
                created_by=user_obj.user_id,
                created_by_name=user_obj.username,
                description="캠페인 일시 정지",
            )

            if query.count() > 0:
                # 00상태의 row 예약 상태 변경 "21"
                # to_status : s1 일시중지
                message_coltroller = MessageReserveController(
                    config["dag_user"], config["dag_access"]
                )
                background_var = {
                    "camp_id": campaign_id,
                    "test_send_yn": "n",
                    "to_status": to_status,
                }
                background_task.add_task(
                    message_coltroller.execute_dag, "nepasend_cancel_resv", background_var
                )

        # 진행대기 -> 운영 **campaign-dag**
        elif (from_status == CampaignStatus.pending.value) and (
            to_status == CampaignStatus.ongoing.value
        ):

            approval_status = CampaignApprovalStatus.APPROVED.value
            approval_obj = self.get_campaign_approval_obj(db, campaign_id, approval_status)
            if not approval_obj:
                raise NotFoundException(detail={"message": "승인 정보를 찾지 못했습니다."})
            approval_no = approval_obj.approval_no

            created_at = localtime_converter()
            res = self.save_campaign_logs(
                db=db,
                campaign_id=campaign_id,
                timeline_type="campaign_event",
                created_at=created_at,
                created_by=user_obj.user_id,
                created_by_name=user_obj.username,
                description="캠페인 시작",
            )
            # 아래 작업은 별도 API에서 진행
            # recipient update
            # 발송예약
            # nepasend_insert_resv

        # --운영중 -> 진행중지(s1)
        elif (from_status == CampaignStatus.ongoing.value) and (
            to_status == CampaignStatus.haltafter.value
        ):

            approval_status = CampaignApprovalStatus.APPROVED.value
            approval_obj = self.get_campaign_approval_obj(db, campaign_id, approval_status)
            if not approval_obj:
                raise NotFoundException(detail={"message": "승인 정보를 찾지 못했습니다."})
            approval_no = approval_obj.approval_no

            tz = "Asia/Seoul"
            korea_timezone = pytz.timezone(tz)
            current_korea_timestamp = datetime.now(korea_timezone)
            current_korea_date = current_korea_timestamp.strftime("%Y%m%d")
            current_korea_timestamp_plus_10_minutes = current_korea_timestamp + timedelta(
                minutes=10
            )  # 발송 10분 전부터 취소 불가능
            query = db.query(SendReservationEntity.set_group_msg_seq).filter(
                SendReservationEntity.campaign_id == campaign_id,
                SendReservationEntity.test_send_yn == "n",
            )

            # 발송 취소 불가 case 1
            cancel_allowed_check_cond = [
                SendReservationEntity.send_resv_date > current_korea_timestamp,
                SendReservationEntity.send_resv_date <= current_korea_timestamp_plus_10_minutes,
                SendReservationEntity.send_resv_state == "01",  # 발송요청
            ]
            cancel_allowed_check = query.filter(*cancel_allowed_check_cond)
            if cancel_allowed_check.count() > 0:
                raise PolicyException(
                    detail={
                        "code": "send_resv/halt/denied/01",
                        "message": "발송 10분 전에는 캠페인을 중지할 수 없습니다.",
                    },
                )

            # 발송 취소 불가 case 2
            cancel_allowed_check_cond_2 = [
                SendReservationEntity.send_resv_date <= current_korea_timestamp,
                SendReservationEntity.send_resv_state == "01",  # 발송요청
            ]
            cancel_allowed_check_2 = query.filter(*cancel_allowed_check_cond_2)
            if cancel_allowed_check_2.count() > 0:
                raise PolicyException(
                    detail={
                        "code": "send_resv/halt/denied/02",
                        "message": "발송 진행 중인 메세지가 존재하여 캠페인 진행을 중지할 수 없습니다.",
                    },
                )

            # 아직 발송 예약 시간이 도래하지 않았고, 발송 요청인 상태의 메세지에 대해 진행 중지를 한다.
            cancel_allowed_cond = [
                SendReservationEntity.send_resv_date > current_korea_timestamp,
                SendReservationEntity.send_resv_state == "01",  # 발송요청
            ]
            cancel_query = query.filter(*cancel_allowed_cond)
            if cancel_query.count() > 0:
                # 발송 취소 로깅

                # offer cus list delete
                # 리마인드 메세지를 중지할 경우에는 오퍼 적용대상을 삭제할 수 없음
                send_msg_types = cancel_query.first()
                if send_msg_types:
                    if send_msg_types.msg_category == "campaign":
                        stmt_1 = delete(OfferCustEntity).where(
                            OfferCustEntity.campaign_id == campaign_id
                        )
                        db.execute(stmt_1)

                message_coltroller = MessageReserveController(
                    config["dag_user"], config["dag_access"]
                )
                # 취소 dag execute (s2) : 미발송메세지 send_reservation 삭제 & nepa_send 삭제
                background_var = {
                    "camp_id": campaign_id,
                    "test_send_yn": "n",
                    "to_status": to_status,
                }
                message_coltroller.execute_dag("nepasend_cancel_resv", background_var)

            else:
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

        # --일시중지-> 진행대기
        elif (from_status == CampaignStatus.haltbefore.value) and (
            to_status == CampaignStatus.pending.value
        ):

            approval_status = CampaignApprovalStatus.APPROVED.value
            approval_obj = self.get_campaign_approval_obj(db, campaign_id, approval_status)
            if not approval_obj:
                raise NotFoundException(detail={"message": "승인 정보를 찾지 못했습니다."})
            approval_no = approval_obj.approval_no

            # "21" -> "00"
            db.query(SendReservationEntity).filter(
                SendReservationEntity.campaign_id == campaign_id,
                SendReservationEntity.test_send_yn == "n",
            ).update({SendReservationEntity.send_resv_state: "00"})

            db.commit()

            # airflow trigger api to nepasend
            message_coltroller = MessageReserveController(config["dag_user"], config["dag_access"])
            background_var = {"camp_id": campaign_id, "test_send_yn": "n"}
            background_task.add_task(
                message_coltroller.execute_dag, "nepasend_insert_resv", background_var
            )

        # --일시중지->임시저장 (예약 삭제 & nepasend 삭제,  validation: "11"상태 row가 존재하는지)
        elif (from_status == CampaignStatus.haltbefore.value) and (
            to_status == CampaignStatus.tempsave.value
        ):

            # campaign_approvals 해당 approval_status를 canceled로 변경
            approval_no = self.cancel_campaign_approval(db, campaign_id)

            # 예약 삭제 & nepasend 삭제
            # to_status : r1 임시저장
            message_coltroller = MessageReserveController(config["dag_user"], config["dag_access"])
            background_var = {"camp_id": campaign_id, "test_send_yn": "n", "to_status": to_status}
            background_task.add_task(
                message_coltroller.execute_dag, "nepasend_cancel_resv", background_var
            )

        # --진행중지->수정 단계 ("r2")
        elif (from_status == CampaignStatus.haltafter.value) and (
            to_status == CampaignStatus.modify.value
        ):

            approval_status = CampaignApprovalStatus.APPROVED.value
            approval_obj = self.get_campaign_approval_obj(db, campaign_id, approval_status)
            if not approval_obj:
                raise NotFoundException(detail={"message": "승인 정보를 찾지 못했습니다."})
            approval_no = approval_obj.approval_no

        # --수정 단계->진행중지 ("s2")
        # send_reservation을 업데이트하고 새로 인서트한다.
        elif (from_status == CampaignStatus.modify.value) and (
            to_status == CampaignStatus.haltafter.value
        ):

            approval_status = CampaignApprovalStatus.APPROVED.value
            approval_obj = self.get_campaign_approval_obj(db, campaign_id, approval_status)
            if not approval_obj:
                raise NotFoundException(detail={"message": "승인 정보를 찾지 못했습니다."})
            approval_no = approval_obj.approval_no

            modify_resv_sync = ModifyReservSync(db, str(user_obj.user_id), campaign_id)
            current_korea_date = datetime.now(selected_timezone).strftime("%Y%m%d")

            result = modify_resv_sync.get_reserve_msgs(current_korea_date)

            if isinstance(result, dict):
                print(result)
                return approval_no
            else:
                msg_seqs_to_save = result
                # insert to send_reservation : 이미 예약한 메세지를 제외하고 예약하기
                res = self.save_campaign_reservation(db, user_obj, campaign_id, msg_seqs_to_save)
                # background_task.add_task(save_campaign_reservation, db, user_obj, campaign_id, msg_seqs_to_save)

                if res:
                    return approval_no
                else:
                    txt = f"{campaign_id} : 당일({current_korea_date}) 정상 예약 메세지가 존재하지 않습니다."
                    print(txt)

        # --진행중지->운영 ("21" 상태의 row 예약 상태 변경 "00")
        elif (from_status == CampaignStatus.haltafter.value) and (
            to_status == CampaignStatus.ongoing.value
        ):

            approval_status = CampaignApprovalStatus.APPROVED.value
            approval_obj = self.get_campaign_approval_obj(db, campaign_id, approval_status)
            if not approval_obj:
                raise NotFoundException(detail={"message": "승인 정보를 찾지 못했습니다."})
            approval_no = approval_obj.approval_no

            # offer_custs insert
            send_msg_types = (
                db.query(SendReservationEntity.msg_category)
                .filter(
                    SendReservationEntity.campaign_id == campaign_id,
                    SendReservationEntity.test_send_yn == "n",
                    SendReservationEntity.send_resv_state == "00",
                )
                .first()
            )

            if send_msg_types:
                if send_msg_types.msg_category == "campaign":
                    save_offer_custs(db, user_obj, campaign_id, background_task)
                # background_task.add_task(save_offer_custs.py, db, user_obj, campaign_id, background_task)

            # airflow trigger api to nepasend
            message_coltroller = MessageReserveController(config["dag_user"], config["dag_access"])
            background_var = {"camp_id": campaign_id, "test_send_yn": "n"}
            message_coltroller.execute_dag("nepasend_insert_resv", background_var)

        # 진행중지, 운영중 -> 완료, 기간만료 **campaign-dag**
        elif (
            from_status
            in (
                CampaignStatus.ongoing.value,
                CampaignStatus.pending.value,
                CampaignStatus.haltbefore.value,
                CampaignStatus.haltafter.value,
            )
        ) and (
            (to_status == CampaignStatus.complete.value)
            or (to_status == CampaignStatus.expired.value)
        ):

            approval_status = CampaignApprovalStatus.APPROVED.value
            approval_obj = self.get_campaign_approval_obj(db, campaign_id, approval_status)
            if not approval_obj:
                raise NotFoundException(detail={"message": "승인 정보를 찾지 못했습니다."})
            approval_no = approval_obj.approval_no

            # ongoing → complete: 완료
            # haltbefore, haltafter → expired : 기간 만료
            created_at = localtime_converter()
            res = self.save_campaign_logs(
                db=db,
                campaign_id=campaign_id,
                timeline_type="campaign_event",
                created_at=created_at,
                created_by=user_obj.user_id,
                created_by_name=user_obj.username,
                description="캠페인 종료",
            )

        else:
            raise ValueError("Invalid status change")

        return approval_no

    def today_approval_campaign_excute(
        self,
        db,
        from_status,
        to_status,  # o1
        campaign_id,
        created_at,
        created_by,
        created_by_name,
        user_obj,
        background_task,
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
        res = self.save_campaign_logs(
            db=db,
            campaign_id=campaign_id,
            timeline_type="campaign_event",
            created_at=created_at,
            created_by=created_by,
            created_by_name=created_by_name,
            description="캠페인 시작",
        )

        # 캠페인 타임라인 로그 저장(2) - 운영중
        res = self.save_campaign_logs(
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
        res = self.save_campaign_reservation(db, user_obj, campaign_id)
        # background_task.add_task(save_campaign_reservation, db, user_obj, campaign_id)

        # offer_cust update campaign_id cus_cd event_no
        # to-do : 취소
        print("offer_custs_insert")
        save_offer_custs(db, user_obj, campaign_id, background_task)
        # background_task.add_task(save_offer_custs.py, db, user_obj, campaign_id, background_task)

        if res:
            # airflow trigger api to nepasend
            message_controller = MessageReserveController()
            input_var = {"campaign_id": campaign_id, "test_send_yn": "n"}
            message_controller.execute_dag("send_messages", input_var)

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
