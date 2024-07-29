from datetime import datetime, timedelta

from fastapi import HTTPException
from sqlalchemy.orm import Session

from src.campaign.enums.campagin_status import CampaignStatus
from src.campaign.enums.campaign_approval_status import CampaignApprovalStatus
from src.campaign.enums.campaign_progress import CampaignProgress
from src.campaign.enums.campaign_timeline_type import CampaignTimelineType
from src.campaign.infra.entity.approver_entity import ApproverEntity
from src.campaign.infra.entity.campaign_approval_entity import CampaignApprovalEntity
from src.campaign.infra.entity.campaign_entity import CampaignEntity
from src.campaign.infra.entity.campaign_remind_entity import CampaignRemindEntity
from src.campaign.infra.entity.campaign_set_groups_entity import CampaignSetGroupsEntity
from src.campaign.infra.entity.campaign_sets_entity import CampaignSetsEntity
from src.campaign.infra.entity.campaign_status_history_entity import (
    CampaignStatusHistoryEntity,
)
from src.campaign.infra.entity.set_group_messages_entity import SetGroupMessagesEntity
from src.campaign.infra.sqlalchemy_query.recurring_campaign.recurring_create import (
    recurring_create,
)
from src.campaign.routes.port.approve_campaign_usecase import ApproveCampaignUseCase
from src.campaign.routes.port.create_recurring_campaign_usecase import (
    CreateRecurringCampaignUseCase,
)
from src.campaign.service.port.base_campaign_repository import BaseCampaignRepository
from src.campaign.service.port.base_campaign_set_repository import (
    BaseCampaignSetRepository,
)
from src.common.timezone_setting import selected_timezone
from src.common.utils import repeat_date
from src.common.utils.data_converter import DataConverter
from src.common.utils.date_utils import calculate_remind_date, localtime_converter
from src.core.exceptions.exceptions import ConsistencyException, NotFoundException
from src.core.transactional import transactional
from src.users.domain.user import User
from src.users.infra.entity.user_entity import UserEntity


class CreateRecurringCampaign(CreateRecurringCampaignUseCase):

    def __init__(
        self,
        campaign_repository: BaseCampaignRepository,
        campaign_set_repository: BaseCampaignSetRepository,
        approve_campaign_service: ApproveCampaignUseCase,
    ):
        self.campaign_repository = campaign_repository
        self.campaign_set_repository = campaign_set_repository
        self.approve_campaign_service = approve_campaign_service

    @transactional
    def exec(self, campaign_id, user: User, db: Session):
        # user_id, username
        user_id = str(user.user_id)
        user_name = str(user.username)

        # 생성해야될 주기성 캠페인 조회
        org_campaign = (
            db.query(CampaignEntity).filter(CampaignEntity.campaign_id == campaign_id).first()
        )

        if not org_campaign:
            raise NotFoundException(
                detail={"message": f"캠페인({campaign_id})이 존재하지 않습니다."}
            )

        retention_day = org_campaign.retention_day
        if not retention_day:
            raise ConsistencyException(detail={"message": "주기성 캠페인에는 "})

        if self.is_campaign_end(org_campaign):
            return {"campaign_id": "has ended"}

        # 직전 캠페인의 종료일
        create_date = datetime.strptime(org_campaign.end_date, "%Y%m%d")
        create_date = (
            create_date - timedelta(days=int(retention_day)) if retention_day else create_date
        )
        org_campaign_end_date = selected_timezone.localize(create_date)

        # 종료일(end_date) - retention_day
        # 직전 캠페인 종료일 + 1day 가 start_date로 지정됨
        # 캠페인 생성일 != 캠페인 시작일
        tz = "Asia/Seoul"
        start_date, end_date = repeat_date.calculate_dates(
            org_campaign_end_date,
            period=org_campaign.repeat_type,
            week_days=org_campaign.week_days,
            datetosend=(
                int(org_campaign.datetosend) if org_campaign.datetosend else None
            ),  # Null or datetosend
            timezone=tz,  # timezone
        )

        end_date_f = datetime.strptime(end_date, "%Y%m%d")
        end_date = end_date_f + timedelta(days=int(retention_day))
        end_date = end_date.strftime("%Y%m%d")

        current_datetime = localtime_converter()

        base_org_campaign_obj: CampaignEntity = (
            db.query(CampaignEntity)
            .filter(CampaignEntity.campaign_group_id == org_campaign.campaign_group_id)
            .order_by(CampaignEntity.start_date)
            .first()
        )

        new_start_date = create_date + timedelta(days=1)
        campaign_name_prefix = new_start_date.strftime("%y%m%d")

        # campaign_base
        campaign_name = (
            base_org_campaign_obj.campaign_name if base_org_campaign_obj.campaign_name else ""
        )
        cloned_campaign = CampaignEntity(
            campaign_name=campaign_name + "_" + campaign_name_prefix,
            campaign_group_id=org_campaign.campaign_group_id,
            budget=org_campaign.budget,
            campaign_type_code=org_campaign.campaign_type_code,
            campaign_type_name=org_campaign.campaign_type_name,
            medias=org_campaign.medias,
            campaign_status_group_code=CampaignStatus.tempsave.group,
            campaign_status_group_name=CampaignStatus.tempsave.group_description,
            campaign_status_code=CampaignStatus.tempsave.value,  # 캠페인 상태 : 임시저장
            campaign_status_name=CampaignStatus.tempsave.description,
            send_type_code=org_campaign.send_type_code,
            send_type_name=org_campaign.send_type_name,
            repeat_type=org_campaign.repeat_type,
            week_days=org_campaign.week_days,
            send_date=start_date,  #
            is_msg_creation_recurred=org_campaign.is_msg_creation_recurred,
            is_approval_recurred=org_campaign.is_approval_recurred,
            datetosend=org_campaign.datetosend,
            timetosend=org_campaign.timetosend,
            start_date=start_date,  #
            end_date=end_date,  #
            group_end_date=org_campaign.group_end_date,
            has_remind=org_campaign.has_remind,
            campaigns_exc=org_campaign.campaigns_exc,
            strategy_id=org_campaign.strategy_id,
            strategy_theme_ids=org_campaign.strategy_theme_ids,
            is_personalized=org_campaign.is_personalized,
            progress=(
                CampaignProgress.MESSAGE_COMPLETE.value
                if org_campaign.is_approval_recurred is True
                else CampaignProgress.DESCRIPTION_COMPLETE.value
            ),
            # is_approval_recurred: 매주기마다 승인처리를 직접 해야되는지 여부
            msg_delivery_vendor=org_campaign.msg_delivery_vendor,
            shop_send_yn=org_campaign.shop_send_yn,
            retention_day=retention_day,  # 유지기간
            owned_by_dept=org_campaign.owned_by_dept,  # 참조 캠페인 생성 부서
            owned_by_dept_name=org_campaign.owned_by_dept_name,  # 참조 캠페인 생성 부서명
            owned_by_dept_abb_name=org_campaign.owned_by_dept_abb_name,  # 참조 캠페인 생성 부서명 약어
            created_at=current_datetime,
            created_by=user_id,
            created_by_name=user_name,
            updated_at=current_datetime,
            updated_by=user_id,
        )

        # remind
        if org_campaign.has_remind:
            remind_list = [
                {
                    "remind_media": remind.remind_media,
                    "remind_step": remind.remind_step,
                    "remind_duration": remind.remind_duration,
                }
                for remind in org_campaign.remind_list
            ]

            remind_dict_list = self.convert_to_campaign_remind(
                user_id,
                cloned_campaign.send_date,
                end_date,
                remind_list,
                org_campaign.send_type_code,
            )

            # 캠페인 리마인드 정보 생성
            cloned_campaign.remind_list = [
                CampaignRemindEntity(**remind_dict) for remind_dict in remind_dict_list
            ]

        else:
            remind_dict_list = None

        db.add(cloned_campaign)
        db.flush()

        created_at = localtime_converter()
        self.approve_campaign_service.save_campaign_logs(
            db=db,
            campaign_id=cloned_campaign.campaign_id,
            timeline_type="campaign_event",
            created_at=created_at,
            created_by=user_id,
            created_by_name=user_name,
            description="주기성 캠페인 생성",
        )

        db.flush()

        campaign_base_dict = DataConverter.convert_model_to_dict(cloned_campaign)
        campaign_base_dict["remind_list"] = remind_dict_list
        new_campaign_id = campaign_base_dict["campaign_id"]

        campaign_obj_dict = {}
        campaign_obj_dict["base"] = campaign_base_dict

        # 생성해야될 주기성 캠페인의 캠페인 세트 조회
        org_campaign_set = (
            db.query(CampaignSetGroupsEntity, CampaignSetGroupsEntity)
            .join(CampaignSetGroupsEntity)
            .filter(CampaignSetGroupsEntity.campaign_id == campaign_id)
        )

        org_campaign_set_df = DataConverter.convert_query_to_df(org_campaign_set)
        is_msg_creation_recurred = org_campaign.is_msg_creation_recurred

        recurring_create(is_msg_creation_recurred, org_campaign_set_df, campaign_obj_dict, user, db)

        # # [자동승인] 캠페인 승인 & 상태변경(진행대기 or 운영중)  & 타임라인 저장
        if campaign_base_dict["progress"] == CampaignProgress.DESCRIPTION_COMPLETE.value:

            created_at = localtime_converter()
            owned_by_dept = campaign_base_dict["owned_by_dept"]
            status_no = None

            dept_user = (
                db.query(UserEntity).filter(UserEntity.department_id == owned_by_dept).first()
            )
            department_abb_name = dept_user.department_abb_name
            department_name = dept_user.department_name

            # is_confirmed = True, is_used가 모두 False인 set는 제외하는 코드
            set_seqs = (
                db.query(CampaignSetGroupsEntity.set_seq)
                .join(
                    SetGroupMessagesEntity,
                    CampaignSetGroupsEntity.set_group_seq == SetGroupMessagesEntity.set_group_seq,
                )
                .filter(
                    CampaignSetGroupsEntity.campaign_id == campaign_id,
                    SetGroupMessagesEntity.is_used.is_(True),
                )
                .distinct()
                .all()
            )

            for set_seq in set_seqs:
                db.query(CampaignSetsEntity).filter(
                    CampaignSetsEntity.campaign_id == campaign_id,
                    CampaignSetsEntity.set_seq == set_seq[0],
                ).update({CampaignSetsEntity.is_confirmed: True})

            # 캠페인 승인 테이블 저장
            new_approver = CampaignApprovalEntity(
                campaign_id=new_campaign_id,
                requester=user.user_id,
                approval_status=CampaignApprovalStatus.APPROVED.value,  # APPROVED
                created_at=created_at,
                created_by=str(user.user_id),
                updated_at=created_at,  # 생성 시점에 updated_at도 설정
                updated_by=str(user.user_id),
            )
            db.add(new_approver)
            db.flush()

            approval_no = new_approver.approval_no

            # 승인자
            approvers = ApproverEntity(
                campaign_id=new_campaign_id,
                approval_no=approval_no,
                user_id=user.user_id,
                user_name=user.username,
                department_id=owned_by_dept,  # 생성부서
                department_name=department_name,  # 생성부서
                department_abb_name=department_abb_name,  # 생성부서
                is_approved=True,  # 기초값 False
                created_at=created_at,
                created_by=str(user.user_id),
                updated_at=created_at,
                updated_by=str(user.user_id),
            )
            db.add(approvers)

            # 진행대기
            to_status = "w2"

            # 타임라인: 승인처리
            self.approve_campaign_service.save_campaign_logs(
                db=db,
                campaign_id=new_campaign_id,
                timeline_type="approval",
                created_at=created_at,
                created_by=str(user.user_id),
                created_by_name=user.username,
                to_status=to_status,
                status_no=status_no,
            )

            # 캠페인 상태 변경
            campaign_status = CampaignStatus.get_eums()
            campaign_status_input = [
                (i["_value_"], i["desc"], i["group"], i["group_desc"])
                for i in campaign_status
                if i["_value_"] == to_status
            ][0]

            cloned_campaign.campaign_status_code = campaign_status_input[0]
            cloned_campaign.campaign_status_name = campaign_status_input[1]
            cloned_campaign.campaign_status_group_code = campaign_status_input[2]
            cloned_campaign.campaign_status_group_name = campaign_status_input[3]

            # #상태 변경 이력
            status_hist = CampaignStatusHistoryEntity(
                campaign_id=new_campaign_id,
                from_status=campaign_base_dict["campaign_status_code"],
                to_status=to_status,
                created_at=created_at,
                approval_no=approval_no,  # if approval_no 초기값은 None
                created_by=str(user.user_id),
            )
            db.add(status_hist)
            db.flush()
            status_no = status_hist.status_no

            # 타임라인: 상태변경
            self.approve_campaign_service.save_campaign_logs(
                db=db,
                campaign_id=new_campaign_id,
                timeline_type=CampaignTimelineType.STATUS_CHANGE.value,
                created_at=created_at,
                created_by=str(user.user_id),
                created_by_name=user.username,
                to_status=to_status,
                status_no=status_no,
            )

            db.commit()

        return {"campaign_id": new_campaign_id}

    def is_campaign_end(self, org_campaign):
        if org_campaign.group_end_date:
            # 주기성 캠페인 생성 종료
            group_end_date = datetime.strptime(org_campaign.group_end_date, "%Y%m%d")
            current_korea_date = datetime.now(selected_timezone).strftime("%Y%m%d")
            current_korea_date = datetime.strptime(current_korea_date, "%Y%m%d")

            return group_end_date <= current_korea_date

        return False

    def convert_to_campaign_remind(self, user_id, send_date, end_date, remind_list, send_type_code):
        """캠페인 리마인드 인서트 딕셔너리 리스트 생성"""

        remind_dict_list = []
        for remind_elem in remind_list:
            """
            remind_step
            remind_duration
            """
            remind_step_dict = {}

            # insert step & duration
            remind_step_dict.update(remind_elem)

            # 리마인드 발송일 계산
            remind_duration = remind_elem["remind_duration"]
            remind_date = calculate_remind_date(end_date, remind_duration)

            if int(remind_date) == int(send_date):
                raise HTTPException(
                    status_code=400,
                    detail={
                        "code": "campaign/remind/date_validation",
                        "message": "리마인드 발송날짜가 캠페인 발송일과 같습니다. 리마인드 시점을 다시 확인해주세요",
                    },
                )
            if int(remind_date) < int(send_date):
                raise HTTPException(
                    status_code=400,
                    detail={
                        "code": "campaign/remind/date_validation",
                        "message": "리마인드 발송날짜가 캠페인 발송일보다 앞에 있습니다. 리마인드 시점을 다시 확인해주세요",
                    },
                )

            remind_step_dict["remind_date"] = remind_date

            # send_type_code & created_by & updated_by
            time_at = localtime_converter()

            remind_step_dict["send_type_code"] = send_type_code
            remind_step_dict["created_by"] = str(user_id)
            remind_step_dict["updated_by"] = str(user_id)
            remind_step_dict["created_at"] = time_at
            remind_step_dict["updated_at"] = time_at

            remind_dict_list.append(remind_step_dict)

        return remind_dict_list
