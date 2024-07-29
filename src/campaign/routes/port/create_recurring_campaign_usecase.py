import time
from abc import ABC, abstractmethod
from datetime import datetime, timedelta

from sqlalchemy.orm import Session

from src.campaign.enums.campagin_status import CampaignStatus
from src.campaign.enums.campaign_progress import CampaignProgress
from src.campaign.infra.entity.campaign_entity import CampaignEntity
from src.campaign.infra.entity.campaign_remind_entity import CampaignRemindEntity
from src.campaign.infra.entity.campaign_set_groups_entity import CampaignSetGroupsEntity
from src.campaign.infra.entity.campaign_sets_entity import CampaignSetsEntity
from src.campaign.infra.entity.set_group_messages_entity import SetGroupMessagesEntity
from src.common.timezone_setting import selected_timezone
from src.common.utils import repeat_date
from src.common.utils.data_converter import DataConverter
from src.common.utils.date_utils import localtime_converter
from src.core.transactional import transactional
from src.users.domain.user import User
from src.users.infra.entity.user_entity import UserEntity


class CreateRecurringCampaignUseCase(ABC):

    @transactional
    @abstractmethod
    def exec(self, campaign_id, user: User, db: Session):
        start_time = time.time()  # 코드 실행 시작 시간
        time.sleep(1)

        # user_id, username
        user_id = str(user.user_id)  # 7596
        user_name = str(user.username)  # nepaadmin

        # # 생성해야될 주기성 캠페인 조회
        org_campaign: CampaignEntity = (
            db.query(CampaignEntity).filter(CampaignEntity.campaign_id == campaign_id).first()
        )

        retention_day = org_campaign.retention_day
        # start_date, enddate
        tz = "Asia/Seoul"
        if org_campaign.group_end_date:
            # 주기성 캠페인 생성 종료
            group_end_date = datetime.strptime(org_campaign.group_end_date, "%Y%m%d")
            current_korea_date = datetime.now(selected_timezone).strftime("%Y%m%d")
            current_korea_date = datetime.strptime(current_korea_date, "%Y%m%d")

            if group_end_date <= current_korea_date:
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
        start_date, end_date = repeat_date.calculate_dates(
            org_campaign_end_date,
            period=org_campaign.repeat_type,
            week_days=org_campaign.week_days,
            datetosend=(
                int(org_campaign.datetosend) if org_campaign.datetosend else None
            ),  # Null or datetosend
            timezone=tz,  # timezone
        )

        if retention_day:
            end_date_f = datetime.strptime(end_date, "%Y%m%d")
            end_date = end_date_f + timedelta(days=int(retention_day))
            end_date = end_date.strftime("%Y%m%d")

        current_datetime = localtime_converter()

        base_org_campaign_obj = (
            db.query(CampaignEntity)
            .filter(CampaignEntity.campaign_group_id == org_campaign.campaign_group_id)
            .order_by(CampaignEntity.start_date)
            .first()
        )

        new_start_date = create_date + timedelta(days=1)
        campaign_name_prefix = new_start_date.strftime("%y%m%d")

        # campaign_base
        cloned_campaign = CampaignEntity(
            campaign_name=(base_org_campaign_obj.campaign_name) + "_" + campaign_name_prefix,
            campaign_group_id=org_campaign.campaign_group_id,
            budget=org_campaign.budget,
            campaign_type_code=org_campaign.campaign_type_code,
            campaign_type_name=org_campaign.campaign_type_name,
            audience_type_code=org_campaign.audience_type_code,
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
                CampaignProgress.message_complete.value
                if org_campaign.is_approval_recurred is True
                else CampaignProgress.decription_complete.value
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

            remind_dict_list = convert_to_campaign_remind(
                user_id, end_date, remind_list, org_campaign.send_type_code
            )

            # 캠페인 리마인드 정보 생성
            cloned_campaign.remind_list = [
                CampaignRemindEntity(**remind_dict) for remind_dict in remind_dict_list
            ]

        else:
            remind_dict_list = None

        # 새 캠페인 객체를 데이터베이스에 추가합니다.
        db.add(cloned_campaign)
        db.flush()

        # Logging 1 : 캠페인 생성
        created_at = localtime_converter()
        res = save_campaign_logs(
            db=db,
            campaign_id=cloned_campaign.campaign_id,
            timeline_type="campaign_event",
            created_at=created_at,
            created_by=user_id,
            created_by_name=user_name,
            description="주기성 캠페인 생성",
        )
        db.commit()

        campaign_base_dict = DataConverter.convert_model_to_dict(cloned_campaign)
        campaign_base_dict["remind_list"] = remind_dict_list
        new_campaign_id = campaign_base_dict["campaign_id"]

        campaign_obj_dict = {}
        campaign_obj_dict["base"] = campaign_base_dict

        # 생성해야될 주기성 캠페인의 캠페인 세트 조회
        org_campaign_set = (
            db.query(CampaignSetsEntity, CampaignSetGroupsEntity)
            .join(CampaignSetGroupsEntity)
            .filter(CampaignSetsEntity.campaign_id == campaign_id)
        )

        org_campaign_set_df = DataConverter.convert_query_to_df(org_campaign_set)

        # 어드민 유저의 토큰
        # access_token = Authorization.split(" ")[1]
        # headers = {"Authorization": "Bearer " + str(access_token)}

        is_msg_creation_recurred = org_campaign.is_msg_creation_recurred

        # # 주기성 캠페인 세트 , 메세지 생성
        res = create_recurring_campaign_set(
            db, user, headers, is_msg_creation_recurred, org_campaign_set_df, campaign_obj_dict
        )

        # # [자동승인] 캠페인 승인 & 상태변경(진행대기 or 운영중)  & 타임라인 저장
        if campaign_base_dict["progress"] == CampaignProgress.decription_complete.value:

            user_obj = user
            created_at = localtime_converter()
            owned_by_dept = campaign_base_dict["owned_by_dept"]
            status_no = None

            dept_user = db.query(User).filter(UserEntity.department_id == owned_by_dept).first()
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
                    SetGroupMessagesEntity.is_used == True,
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
            new_approver = campaignDB.CampaignApprovals(
                campaign_id=new_campaign_id,
                requester=user_obj.user_id,
                approval_status=enums.CampaignApprovalStatus.APPROVED.value,  # APPROVED
                created_at=created_at,
                created_by=user_obj.user_id,
                updated_at=created_at,  # 생성 시점에 updated_at도 설정
                updated_by=user_obj.user_id,
            )
            db.add(new_approver)
            db.flush()

            approval_no = new_approver.approval_no

            # 승인자
            approvers = campaignDB.Approvers(
                campaign_id=new_campaign_id,
                approval_no=approval_no,
                user_id=user_obj.user_id,  # nepaadmin/dev
                user_name=user_obj.username,  # nepaadmin/dev
                department_id=owned_by_dept,  # 생성부서
                department_name=department_name,  # 생성부서
                department_abb_name=department_abb_name,  # 생성부서
                is_approved=True,  # 기초값 False
                created_at=created_at,
                created_by=user_obj.user_id,
                updated_at=created_at,
                updated_by=user_obj.user_id,
            )
            db.add(approvers)

            to_status = "w2"  # 진행대기

            # 타임라인: 승인처리
            res = save_campaign_logs(
                db=db,
                campaign_id=new_campaign_id,
                timeline_type="approval",
                created_at=created_at,
                created_by=user_obj.user_id,  # nepaadmin/dev
                created_by_name=user_obj.username,  # nepaadmin/dev
                to_status=to_status,
                status_no=status_no,
            )

            # 캠페인 상태 변경
            campaign_status = enums.CampaignStatus.get_eums()
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
            status_hist = campaignDB.CampaignStatusHistory(
                campaign_id=new_campaign_id,
                from_status=campaign_base_dict["campaign_status_code"],
                to_status=to_status,
                created_at=created_at,
                approval_no=approval_no,  # if approval_no 초기값은 None
                created_by=user_obj.user_id,  # nepaadmin/dev
            )
            db.add(status_hist)
            db.flush()
            status_no = status_hist.status_no

            # 타임라인: 상태변경
            res = save_campaign_logs(
                db=db,
                campaign_id=new_campaign_id,
                timeline_type=enums.CampaignTimelineTypeEnum.STATUS_CHANGE.value,
                created_at=created_at,
                created_by=user_obj.user_id,
                created_by_name=user_obj.username,
                to_status=to_status,
                status_no=status_no,
            )

            db.commit()

        end_time = time.time()  # 코드 실행 종료 시간
        elapsed_time = end_time - start_time  # 실행 시간 계산

        print()
        print(f"코드 실행 시간: {elapsed_time}초")

        return {"campaign_id": new_campaign_id}
