from datetime import datetime, timedelta

from fastapi import HTTPException
from sqlalchemy import literal_column
from sqlalchemy.orm import Session

from src.campaign.enums.campagin_status import CampaignStatus
from src.campaign.enums.campaign_approval_status import CampaignApprovalStatus
from src.campaign.enums.campaign_progress import CampaignProgress
from src.campaign.enums.campaign_timeline_type import CampaignTimelineType
from src.campaign.enums.campaign_type import CampaignType
from src.campaign.infra.entity.approver_entity import ApproverEntity
from src.campaign.infra.entity.campaign_approval_entity import CampaignApprovalEntity
from src.campaign.infra.entity.campaign_entity import CampaignEntity
from src.campaign.infra.entity.campaign_remind_entity import CampaignRemindEntity
from src.campaign.infra.entity.campaign_set_groups_entity import CampaignSetGroupsEntity
from src.campaign.infra.entity.campaign_sets_entity import CampaignSetsEntity
from src.campaign.infra.entity.campaign_status_history_entity import (
    CampaignStatusHistoryEntity,
)
from src.campaign.infra.entity.kakao_link_buttons_entity import KakaoLinkButtonsEntity
from src.campaign.infra.entity.message_resource_entity import MessageResourceEntity
from src.campaign.infra.entity.set_group_messages_entity import SetGroupMessagesEntity
from src.campaign.infra.sqlalchemy_query.create_set_group_messages import (
    create_set_group_messages,
)
from src.campaign.infra.sqlalchemy_query.get_set_group_seqs import get_set_group_seqs
from src.campaign.infra.sqlalchemy_query.recurring_campaign.get_campaign_api_logic import (
    get_campaigns_api_logic,
)
from src.campaign.infra.sqlalchemy_query.recurring_campaign.get_data_value import (
    get_data_value,
)
from src.campaign.routes.dto.request.message_generate import MsgGenerationReq
from src.campaign.routes.port.approve_campaign_usecase import ApproveCampaignUseCase
from src.campaign.routes.port.create_recurring_campaign_usecase import (
    CreateRecurringCampaignUseCase,
)
from src.campaign.routes.port.generate_message_usecase import GenerateMessageUsecase
from src.campaign.service.campaign_dependency_manager import CampaignDependencyManager
from src.campaign.service.campaign_manager import CampaignManager
from src.campaign.service.port.base_campaign_repository import BaseCampaignRepository
from src.campaign.service.port.base_campaign_set_repository import (
    BaseCampaignSetRepository,
)
from src.campaign.utils.utils import get_resv_date
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
        generate_message_service: GenerateMessageUsecase,
    ):
        self.campaign_repository = campaign_repository
        self.campaign_set_repository = campaign_set_repository
        self.approve_campaign_service = approve_campaign_service
        self.generate_message_service = generate_message_service

    @transactional
    def exec(self, campaign_id, user: User, db: Session) -> dict:
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
            raise ConsistencyException(
                detail={"message": "주기성 캠페인에 설정된 유지기간이 존재하지 않습니다."}
            )

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

        self.recurring_create(
            is_msg_creation_recurred, org_campaign_set_df, campaign_obj_dict, user, db
        )

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

    def recurring_create(
        self,
        is_msg_creation_recurred,
        org_campaign_set_df,
        campaign_obj_dict,
        user: User,
        db: Session,
    ):
        user_id = user.user_id

        campaign_base_dict = campaign_obj_dict["base"]
        campaign_id = campaign_base_dict["campaign_id"]
        shop_send_yn = campaign_base_dict["shop_send_yn"]

        # 캠페인 오브젝트, 캠페인 세트, Recipient
        if is_msg_creation_recurred is True:
            # custom (캠페인 & Recipient & 캠페인 메세지 생성) <- 참조 캠페인 메세지

            # 캠페인 세트 생성
            recurring_campaign_id = org_campaign_set_df["campaign_id"].values[0]
            campaign_manager = CampaignManager(db, shop_send_yn, user_id, recurring_campaign_id)
            recipient_df = campaign_manager.prepare_campaign_recipients(campaign_base_dict)

            # 수신자 고객 생성
            if recipient_df is not None:
                campaign_manager.update_campaign_recipients(recipient_df)

            db.flush()

            # 메세지 생성
            self.create_recurring_message(
                db, user, user_id, org_campaign_set_df, campaign_id, campaign_base_dict
            )

        else:
            campaigns = self.campaign_repository.get_campaign_detail(campaign_id, user, db)

            selected_themes, strategy_theme_ids = self.campaign_set_repository.create_campaign_set(
                campaigns, str(user.user_id), db
            )

            campaign_type_code = campaigns.campaign_type_code
            strategy_id = campaigns.strategy_id
            campaign_id = campaigns.campaign_id

            # expert 캠페인일 경우 데이터 sync 진행
            campaign_dependency_manager = CampaignDependencyManager(user)

            if campaign_type_code == CampaignType.EXPERT.value:
                campaign_dependency_manager.sync_campaign_base(
                    db, campaign_id, selected_themes, strategy_theme_ids
                )
                campaign_dependency_manager.sync_strategy_status(db, strategy_id)
            campaign_dependency_manager.sync_audience_status(db, campaign_id)

            db.flush()

            # 메시지 생성
            self.create_message(db, user, campaign_id)

        db.commit()

        return True

    def create_recurring_message(
        self, db, user, user_id, org_campaign_set_df, campaign_id, campaign_base_dict
    ):
        # set_group_message
        subquery_1 = (
            db.query(
                CampaignSetGroupsEntity.set_seq,
                CampaignSetGroupsEntity.set_group_seq,
                CampaignSetGroupsEntity.set_sort_num,
                CampaignSetGroupsEntity.group_sort_num,
                literal_column("NULL").label("remind_seq"),
                literal_column("NULL").label("remind_step"),
                literal_column("NULL").label("send_type_code"),
                literal_column("NULL").label("remind_duration"),
                literal_column("NULL").label("remind_date"),
                CampaignEntity.campaign_id,
                CampaignEntity.start_date,
                CampaignEntity.end_date,
                CampaignEntity.send_date,
                CampaignSetGroupsEntity.set_group_category,
                CampaignSetGroupsEntity.set_group_val,
            )
            .join(CampaignEntity, CampaignSetGroupsEntity.campaign_id == CampaignEntity.campaign_id)
            .filter(CampaignSetGroupsEntity.campaign_id == campaign_id)
            .subquery()
        )

        new_campaign_group_remind_msgs = []
        if campaign_base_dict["has_remind"]:
            # set_group_message
            new_campaign_group_remind_msgs = (
                db.query(
                    subquery_1.c.set_seq,
                    subquery_1.c.set_group_seq,
                    subquery_1.c.set_sort_num,
                    subquery_1.c.group_sort_num,
                    CampaignRemindEntity.remind_seq,
                    CampaignRemindEntity.remind_step,
                    CampaignRemindEntity.send_type_code,
                    CampaignRemindEntity.remind_duration,
                    CampaignRemindEntity.remind_date,
                    subquery_1.c.start_date,
                    subquery_1.c.end_date,
                    subquery_1.c.send_date,
                    subquery_1.c.set_group_category,
                    subquery_1.c.set_group_val,
                )
                .outerjoin(
                    CampaignRemindEntity,
                    subquery_1.c.campaign_id == CampaignRemindEntity.campaign_id,
                )
                .filter(subquery_1.c.campaign_id == campaign_id)
                .all()
            )

        new_campaign_group_msgs = db.query(subquery_1).all()

        campaign_type_code = campaign_base_dict["campaign_type_code"]
        is_personalized = campaign_base_dict["is_personalized"]
        audience_type_code = campaign_base_dict["audience_type_code"]
        msg_delivery_vendor = campaign_base_dict["msg_delivery_vendor"]
        has_remind = campaign_base_dict["has_remind"]

        org_campaign_id = org_campaign_set_df["campaign_id"][0]

        org_campaign_msgs = (
            db.query(
                SetGroupMessagesEntity,
                CampaignSetGroupsEntity.set_sort_num,
                CampaignSetGroupsEntity.group_sort_num,
                CampaignSetGroupsEntity.set_group_category,
                CampaignSetGroupsEntity.set_group_val,
            )
            .join(
                SetGroupMessagesEntity,
                SetGroupMessagesEntity.set_group_seq == CampaignSetGroupsEntity.set_group_seq,
            )
            .filter(SetGroupMessagesEntity.campaign_id == org_campaign_id)
            .all()
        )

        msg_objs = get_set_group_seqs(db, campaign_id)
        set_group_seqs = []
        result_dict = {}  # set_seq : [set_group_msg]

        campaign_msg_switch = True

        for group_msg_iter in [new_campaign_group_msgs, new_campaign_group_remind_msgs]:

            for item in group_msg_iter:

                set_seq = item.set_seq
                set_group_seq = item.set_group_seq
                set_sort_num = item.set_sort_num
                group_sort_num = item.group_sort_num
                remind_seq = item.remind_seq
                remind_step = item.remind_step
                remind_date = item.remind_date
                start_date = item.start_date
                send_date = item.send_date
                set_group_category = item.set_group_category
                set_group_val = item.set_group_val

                if campaign_type_code == "basic":
                    # group별 비율로 생성되었으므로
                    # group_sort_num 로 이어 붙이기
                    org_msg = [
                        org_item
                        for org_item in org_campaign_msgs
                        if org_item[1] == set_sort_num
                        and org_item[2] == group_sort_num
                        and org_item[0].remind_step == remind_step
                    ]
                    org_msg = org_msg[0] if len(org_msg) > 0 else None

                elif campaign_type_code == "expert" and audience_type_code == "c":
                    # set_group_val를 그룹으로 나눴으므로
                    # set_group_val 로 이어 붙이기
                    org_msg = [
                        org_item
                        for org_item in org_campaign_msgs
                        if org_item[1] == set_sort_num
                        and org_item[4] == set_group_val
                        and org_item[0].remind_step == remind_step
                    ]
                    org_msg = org_msg[0] if len(org_msg) > 0 else None  # 새로 생긴 그룹의 경우 None

                else:
                    raise ValueError("error")

                if org_msg:
                    # 기존의 메세지와 매칭되는 메세지는 메세지를 복사한다.
                    camp_resv_date = get_resv_date(
                        msg_send_type=org_msg[0].msg_send_type,
                        start_date=start_date,
                        send_date=send_date,
                        remind_date=remind_date,
                    )

                    msg_obj = SetGroupMessagesEntity(
                        set_group_seq=set_group_seq,
                        msg_send_type=org_msg[0].msg_send_type,
                        remind_step=remind_step,
                        remind_seq=remind_seq,
                        msg_resv_date=camp_resv_date,
                        set_seq=set_seq,
                        campaign_id=campaign_id,
                        media=org_msg[0].media,
                        msg_type=org_msg[0].msg_type,
                        msg_title=org_msg[0].msg_title,
                        msg_body=org_msg[0].msg_body,
                        msg_gen_key=org_msg[0].msg_gen_key,
                        rec_explanation=org_msg[0].rec_explanation,
                        bottom_text=org_msg[0].bottom_text,
                        msg_announcement=org_msg[0].msg_announcement,
                        template_id=org_msg[0].template_id,
                        msg_photo_uri=org_msg[0].msg_photo_uri,
                        phone_callback=org_msg[0].phone_callback,
                        is_used=org_msg[0].is_used,
                        created_at=localtime_converter(),
                        created_by=user_id,
                        updated_at=localtime_converter(),
                        updated_by=user_id,
                    )

                    db.add(msg_obj)
                    db.flush()

                    new_msg_seq = msg_obj.set_group_msg_seq
                    org_msg_seq = org_msg[0].set_group_msg_seq

                    # 버튼 링크 kakao_link_buttons
                    button_obj = (
                        db.query(KakaoLinkButtonsEntity)
                        .filter(KakaoLinkButtonsEntity.set_group_msg_seq == org_msg_seq)
                        .all()
                    )

                    for button_item in button_obj:
                        button_obj = KakaoLinkButtonsEntity(
                            set_group_msg_seq=new_msg_seq,
                            button_name=button_item.button_name,
                            button_type=button_item.button_type,
                            web_link=button_item.web_link,
                            app_link=button_item.app_link,
                            created_at=localtime_converter(),
                            created_by=user_id,
                            updated_at=localtime_converter(),
                            updated_by=user_id,
                        )

                        db.add(button_obj)

                    # 메세지 message_image_resources
                    msg_img_obj = (
                        db.query(MessageResourceEntity)
                        .filter(MessageResourceEntity.set_group_msg_seq == org_msg_seq)
                        .all()
                    )

                    for msg_img_item in msg_img_obj:
                        msg_img_obj = MessageResourceEntity(
                            set_group_msg_seq=new_msg_seq,
                            resource_name=msg_img_item.resource_name,
                            resource_path=msg_img_item.resource_path,
                            img_uri=msg_img_item.img_uri,
                            link_url=msg_img_item.link_url,
                            landing_url=msg_img_item.landing_url,
                        )

                        db.add(msg_img_obj)

                else:
                    # 기본캠페인 , expert-custom
                    # 새로 생긴 group에 대한 메세지는 새로 생성한다.
                    # 메세지 기본 정보 생성
                    set_msg_list = []
                    for row in msg_objs:
                        if row._asdict()["set_group_seq"] == set_group_seq:
                            elem_msg_seq = row._asdict()
                            set_group_seqs.append(elem_msg_seq)
                            set_msg_list.append(elem_msg_seq)

                            set_seq = row._asdict()["set_seq"]

                            if set_seq not in result_dict:
                                result_dict[set_seq] = set_msg_list
                            else:
                                result_dict[set_seq].extend(set_msg_list)

        if len(set_group_seqs) > 0:
            create_set_group_messages(
                db,
                user_id,
                campaign_id,
                msg_delivery_vendor,
                start_date,
                send_date,
                has_remind,
                set_group_seqs,
                campaign_type_code,
            )

            # 캠페인 base
            campaign_get_resp = get_campaigns_api_logic(db, campaign_id)
            campaign_base = campaign_get_resp["base"]

            # # 메세지 생성 : msg_generation
            for res_set_seq, set_group_message_list in result_dict.items():
                # 해당 세트 내 새로 생성해야되는 set_msg_elem
                set_object = [
                    set_elem
                    for set_elem in campaign_get_resp["set_list"]
                    if set_elem["set_seq"] == res_set_seq
                ][0]
                set_groups = [
                    set_group
                    for set_group in campaign_get_resp["set_group_list"]
                    if set_group["set_seq"] == res_set_seq
                ]
                set_group_msg_seqs = get_data_value(set_group_message_list, "set_group_msg_seq")

                msg_generation_req = MsgGenerationReq(
                    campaign_base=campaign_base,
                    set_object=set_object,  #
                    set_group_list=set_groups,
                    req_generate_msg_seq=set_group_msg_seqs,
                )

                self.generate_message_service.generate_message(msg_generation_req, user)

                # # 캠페인 세트 메세지 검토 : is_message_confirmed
                db.query(CampaignSetsEntity).filter(
                    CampaignSetsEntity.campaign_id == campaign_id,
                    CampaignSetsEntity.set_seq == res_set_seq,
                ).update({CampaignSetsEntity.is_message_confirmed: True})

        db.commit()

        return True

    def create_message(self, db, user, campaign_id):
        # # 캠페인 조회
        campaign_get_resp = get_campaigns_api_logic(db, campaign_id)
        campaign_base = campaign_get_resp["base"]

        # # 메세지 생성 : msg_generation
        set_seqs = []
        req_body = {}
        for set_object in campaign_get_resp["set_list"]:
            set_seq = set_object["set_seq"]
            set_groups = [
                set_group
                for set_group in campaign_get_resp["set_group_list"]
                if set_group["set_seq"] == set_seq
            ]
            set_group_message_list = campaign_get_resp["set_group_message_list"][int(set_seq)]
            set_group_msg_seqs = get_data_value(set_group_message_list, "set_group_msg_seq")

            msg_generation_req = MsgGenerationReq(
                campaign_base=campaign_base,
                set_object=set_object,
                set_group_list=set_groups,
                req_generate_msg_seq=set_group_msg_seqs,
            )

            self.generate_message_service.generate_message(msg_generation_req, user)

            # # 캠페인 세트 메세지 검토 : is_message_confirmed
            db.query(CampaignSetsEntity).filter(
                CampaignSetsEntity.campaign_id == campaign_id, CampaignSetsEntity.set_seq == set_seq
            ).update({CampaignSetsEntity.is_message_confirmed: True})

        db.commit()

        return True
