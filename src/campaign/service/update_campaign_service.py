import json
from datetime import datetime, timedelta

import pandas as pd
from sqlalchemy import and_, delete, func, update
from sqlalchemy.orm import Session

from src.auth.infra.entity.message_integration_entity import MessageIntegrationEntity
from src.campaign.enums.campagin_status import CampaignStatus
from src.campaign.enums.campaign_timeline_type import CampaignTimelineType
from src.campaign.enums.campaign_type import CampaignType
from src.campaign.enums.send_type import SendTypeEnum
from src.campaign.infra.entity.campaign_entity import CampaignEntity
from src.campaign.infra.entity.campaign_remind_entity import CampaignRemindEntity
from src.campaign.infra.entity.campaign_timeline_entity import CampaignTimelineEntity
from src.campaign.infra.entity.send_reservation_entity import SendReservationEntity
from src.campaign.infra.entity.set_group_messages_entity import SetGroupMessagesEntity
from src.campaign.infra.sqlalchemy_query.add_set_rep_contents import (
    add_set_rep_contents,
)
from src.campaign.infra.sqlalchemy_query.get_campaign_set_groups import (
    get_campaign_set_groups,
)
from src.campaign.infra.sqlalchemy_query.get_campaign_sets import get_campaign_sets
from src.campaign.infra.sqlalchemy_query.modify_reservation_sync_service import (
    ModifyReservSync,
)
from src.campaign.infra.sqlalchemy_query.recurring_campaign.convert_to_set_group_message_list import (
    convert_to_set_group_message_list,
)
from src.campaign.infra.sqlalchemy_query.recurring_campaign.get_campaign_set_group_messages import (
    get_campaign_set_group_messages,
)
from src.campaign.infra.sqlalchemy_query.recurring_campaign.get_set_portion import (
    get_set_portion,
)
from src.campaign.routes.dto.request.campaign_create import CampaignCreate
from src.campaign.routes.port.update_campaign_usecase import UpdateCampaignUseCase
from src.campaign.service.authorization_checker import AuthorizationChecker
from src.campaign.service.campaign_dependency_manager import CampaignDependencyManager
from src.campaign.service.campaign_manager import CampaignManager
from src.campaign.service.port.base_campaign_repository import BaseCampaignRepository
from src.campaign.utils.utils import set_summary_sentence
from src.common.enums.campaign_media import CampaignMedia
from src.common.timezone_setting import selected_timezone
from src.common.utils import repeat_date
from src.common.utils.date_utils import calculate_remind_date
from src.core.exceptions.exceptions import PolicyException
from src.core.transactional import transactional
from src.message_template.enums.message_type import MessageType
from src.user.domain.user import User


class UpdateCampaignService(UpdateCampaignUseCase):

    def __init__(self, campaign_repository: BaseCampaignRepository):
        self.campaign_repository = campaign_repository

    @transactional
    def exec(
        self, campaign_id: str, campaign_update: CampaignCreate, user: User, db: Session
    ) -> dict:

        campaign: CampaignEntity = (
            db.query(CampaignEntity).filter(CampaignEntity.campaign_id == campaign_id).first()
        )

        print("campaign.remind_list")
        print(campaign.remind_list)

        if campaign.campaign_status_code == "r1":
            campaign_schema_obj, remind_dict_list = self.update_campaign_with_remind(
                db, user, campaign_update, campaign
            )
        elif campaign.campaign_status_code == "r2":
            campaign_schema_obj, remind_dict_list = self.update_campaign_obj_modification(
                db, user, campaign_update, campaign
            )
        else:
            raise PolicyException(detail={"message": "캠페인을 수정할 수 없는 상태입니다."})

        self.save_campaign_logs(
            db=db,
            campaign_id=campaign_id,
            timeline_type="campaign_event",
            created_by=user.user_id,
            created_by_name=user.username,
            description="캠페인 변경",
        )

        if not self.is_updatable(campaign, user):
            raise PolicyException(detail={"message": "캠페인을 수정할 수 없습니다."})

        user_id = user.user_id
        campaign_base_dict = campaign.as_dict()
        shop_send_yn = campaign_base_dict["shop_send_yn"]
        req_campaigns_exc = campaign_update.campaigns_exc if campaign_update.campaigns_exc else []
        req_audiences_exc = campaign_update.audiences_exc if campaign_update.audiences_exc else []
        base_campaigns_exc = (
            []
            if campaign_base_dict.get("campaigns_exc") is None
            else campaign_base_dict.get("campaigns_exc")
        )
        base_audiences_exc = (
            []
            if campaign_base_dict.get("audiences_exc") is None
            else campaign_base_dict.get("audiences_exc")
        )

        if (set(base_campaigns_exc) != set(req_campaigns_exc)) or (
            set(base_audiences_exc) != set(req_audiences_exc)
        ):
            campaign_base_dict["campaigns_exc"] = req_campaigns_exc
            campaign.campaigns_exc = req_campaigns_exc
            campaign_base_dict["audiences_exc"] = req_audiences_exc
            campaign.audiences_exc = req_audiences_exc
            campaign_manager = CampaignManager(db, shop_send_yn, user_id)
            recipient_df = campaign_manager.prepare_campaign_recipients(campaign_base_dict)
            if recipient_df is not None:
                campaign_manager.update_campaign_recipients(recipient_df)
        db.flush()

        if campaign.campaign_type_code == CampaignType.EXPERT.value:
            sets = [row._asdict() for row in get_campaign_sets(db=db, campaign_id=campaign_id)]
            set_groups = [
                row._asdict() for row in get_campaign_set_groups(db=db, campaign_id=campaign_id)
            ]

            sets = add_set_rep_contents(sets, set_groups, campaign_id, db)
            set_group_messages = get_campaign_set_group_messages(db=db, campaign_id=campaign_id)
            set_group_message_list = convert_to_set_group_message_list(set_group_messages)
            recipient_portion, _, set_cus_count = get_set_portion(campaign_id, db)
            set_df = pd.DataFrame(sets)
            recipient_descriptions = set_summary_sentence(set_cus_count, set_df)

        else:  # 기본 캠페인
            recipient_portion = 0
            recipient_descriptions = None
            sets = None
            set_groups = None
            set_group_message_list = None

        return {
            "progress": campaign.progress,
            "base": campaign.as_dict(),
            "set_summary": {
                "recipient_portion": recipient_portion,
                "recipient_descriptions": recipient_descriptions,
            },
            "set_list": sets,
            "set_group_list": set_groups,
            "set_group_message_list": set_group_message_list,
        }

    def is_updatable(self, campaign, user):
        authorization_checker = AuthorizationChecker(user)
        campaign_dependency_manager = CampaignDependencyManager(user)

        object_role_access = authorization_checker.object_role_access()
        object_department_access = authorization_checker.object_department_access(campaign)
        is_object_updatable = campaign_dependency_manager.is_object_updatable(campaign)
        if object_department_access + object_role_access == 0:
            raise PolicyException(
                detail={
                    "code": "campaign/update/denied/access",
                    "message": "수정 권한이 존재하지 않습니다.",
                },
            )
        else:
            # 권한이 있는 경우
            if not is_object_updatable:
                raise PolicyException(
                    detail={
                        "code": "campaign/update/denied/status",
                        "message": "캠페인이 임시저장 상태가 아닙니다.",
                    },
                )
        return True

    def save_campaign_logs(
        self,
        db,
        campaign_id,
        timeline_type,
        created_by,
        created_by_name,
        description,
        to_status=None,
        status_no=None,
        approval_excute=None,
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
            created_by=created_by,
            created_by_name=created_by_name,
        )

        db.add(timelines)

    def update_campaign_with_remind(
        self, db, user, campaign_update: CampaignCreate, campaign_base: CampaignEntity
    ):
        """캠페인 업데이트 반영
        - campaign_base: 캠페인 기본 정보 (Base 모델)
        - campaign_update_obj: 업데이트 정보 (pydantic 모델)
        """

        # 유저정보
        user_obj = user
        user_id = user_obj.user_id
        department_id = user_obj.department_id

        # 캠페인 Validation
        if campaign_base.campaign_type_code != campaign_update.campaign_type_code.value:
            raise PolicyException(
                detail={
                    "code": "campaign_type/update/denied",
                    "message": "캠페인 타입은 변경할 수 없습니다.",
                },
            )

        if campaign_base.send_type_code != campaign_update.send_type_code.value:
            raise PolicyException(
                detail={
                    "code": "send_type/update/denied",
                    "message": "발송 형태는 변경할 수 없습니다.",
                },
            )

        # update 정보 변경
        campaign_base.updated_by = str(user_id)
        campaign_base.owned_by_dept = department_id

        # 캠페인 이름
        if campaign_base.campaign_name != campaign_update.campaign_name:
            campaign_base.campaign_name = campaign_update.campaign_name
            print(
                f"캠페인 이름 변경: {campaign_base.campaign_name} -> {campaign_update.campaign_name}"
            )

        # 발송 매체
        if campaign_base.medias != campaign_update.medias:
            campaign_base.medias = campaign_update.medias
            print(f"발송 매체 변경: {campaign_base.medias} -> {campaign_update.medias}")

        # print(getattr(campaign_base))
        date_keys = [
            "start_date",
            "end_date",
            "send_date",
            "timetosend",
            "week_days",
            "group_end_date",
            "datetosend",
            "repeat_type",
        ]

        campaign_req_json = campaign_update.json()
        campaign_req_json = json.loads(campaign_req_json)
        changed_values = {
            key: campaign_req_json[key]
            for key in date_keys
            if campaign_req_json[key] != getattr(campaign_base, key)
        }

        print(changed_values)
        is_date_values_changed = len(changed_values) > 0
        if is_date_values_changed:
            if campaign_update.send_type_code == SendTypeEnum.RECURRING.value:
                # 주기성 캠페인 정보 갱신
                create_date = datetime.now(selected_timezone)
                # Todo: 추후 주기성에서 시작일자 부여되면 반영
                start_date, end_date = repeat_date.calculate_dates(
                    create_date,
                    period=campaign_update.repeat_type,
                    week_days=campaign_update.week_days,
                    datetosend=campaign_update.datetosend,
                    timezone="Asia/Seoul",  # timezone
                )
                # retention_day 적용 후 end_date 생성
                retention_day = campaign_update.retention_day
                if retention_day:
                    end_date_f = datetime.strptime(end_date, "%Y%m%d")
                    end_date = end_date_f + timedelta(days=int(retention_day))
                    end_date = end_date.strftime("%Y%m%d")

                campaign_base.group_end_date = campaign_update.group_end_date

                # 시작 종료일이 다르면 갱신
                campaign_base.start_date = start_date
                campaign_base.end_date = end_date
                campaign_base.send_date = start_date
                campaign_base.datetosend = campaign_update.datetosend
                campaign_base.repeat_type = campaign_update.repeat_type
                campaign_base.timetosend = campaign_update.timetosend
                campaign_base.week_days = campaign_update.week_days
                campaign_base.group_end_date = campaign_update.group_end_date
                campaign_base.is_approval_recurred = campaign_update.is_approval_recurred
                campaign_base.is_msg_creation_recurred = campaign_update.is_msg_creation_recurred
            else:
                # 일회성에서는 시작일과 종료일 존재
                campaign_base.start_date = campaign_update.start_date
                campaign_base.end_date = campaign_update.end_date
                campaign_base.send_date = campaign_update.send_date
                campaign_base.timetosend = campaign_update.timetosend
                end_date = campaign_update.end_date

            # 발송일이 변경되면 메시지 오브젝트도 변경
            if "send_date" in changed_values:
                set_group_msg_obj = (
                    db.query(SetGroupMessagesEntity)
                    .filter(SetGroupMessagesEntity.campaign_id == campaign_base.campaign_id)
                    .all()
                )
                for msg_obj in set_group_msg_obj:
                    if msg_obj.msg_send_type == "campaign":
                        msg_obj.msg_resv_date = campaign_update.send_date
                        msg_obj.updated_by = str(user_id)

        else:
            end_date = campaign_base.end_date

        # 캠페인 리마인드 체크
        req_remind_update = campaign_update.remind_list

        send_type_code = campaign_update.send_type_code

        remind_dict_list = None
        # remind 정보가 있다면 반드시 End_date가 존재해야함
        if req_remind_update or campaign_base.remind_list:
            remind_dict_list = self.convert_to_campaign_remind(
                user_id, campaign_base.send_date, end_date, req_remind_update, send_type_code
            )
            campaign_base = self.update_remind_obj(db, campaign_base, remind_dict_list)

        db.add(campaign_base)
        db.flush()

        return campaign_base, remind_dict_list

    def update_campaign_obj_modification(self, db, user, campaign_update_obj, campaign_base):
        """캠페인 "수정단계" 업데이트 반영
        - campaign_base: 캠페인 기본 정보 (Base 모델)
        - campaign_update_obj: 업데이트 정보 (pydantic 모델)
        """

        # 유저정보
        user_obj = user
        user_id = user_obj.user_id
        department_id = user_obj.department_id

        # pydantic모델 ->dictionary
        campaign_req_json = campaign_update_obj.json()
        campaign_req_json = json.loads(campaign_req_json)
        print("campaign_req_json")
        print(campaign_req_json)

        # 캠페인 Validation
        if campaign_base.campaign_type_code != campaign_update_obj.campaign_type_code.value:
            raise PolicyException(
                detail={
                    "code": "campaign_type/update/denied",
                    "message": "캠페인 타입은 변경할 수 없습니다.",
                },
            )
        tz = "Asia/Seoul"
        if campaign_base.send_type_code != campaign_update_obj.send_type_code.value:
            raise PolicyException(
                detail={
                    "code": "send_type/update/denied",
                    "message": "발송 형태는 변경할 수 없습니다.",
                },
            )
        # update 정보 변경
        campaign_base.updated_by = str(user_id)
        campaign_base.owned_by_dept = department_id

        # 캠페인 이름
        if campaign_base.campaign_name != campaign_update_obj.campaign_name:
            raise PolicyException(
                detail={
                    "code": "send_type/update/denied",
                    "message": "수정 단계에서 캠페인명을 변경할 수 없습니다.",
                },
            )
        # 발송 매체
        if campaign_base.medias != campaign_update_obj.medias:
            raise PolicyException(
                detail={
                    "code": "send_type/update/denied",
                    "message": "수정 단계에서 발송 매체를 변경할 수 없습니다.",
                },
            )

        # 발송한 캠페인은 start_date, end_date를 수정할 수 없음
        # 발송시도 완료된 메세지가져오기
        send_complete_msgs_query = db.query(
            func.distinct(SendReservationEntity.set_group_msg_seq)
        ).filter(
            SendReservationEntity.campaign_id == campaign_base.campaign_id,
            SendReservationEntity.test_send_yn == "n",
            SendReservationEntity.send_resv_state.not_in(["01", "00", "21"]),  # 발송한 메세지 추출
        )
        send_complete_msgs = list(send_complete_msgs_query)

        date_keys = [
            "start_date",
            "end_date",
            "send_date",
            "timetosend",
            "week_days",
            "group_end_date",
            "datetosend",
            "repeat_type",
        ]
        changed_values = {
            key: campaign_req_json[key]
            for key in date_keys
            if campaign_req_json[key] != getattr(campaign_base, key)
        }
        is_date_values_changed = len(changed_values) > 0
        modify_resv_sync = ModifyReservSync(db, str(user_id), campaign_base.campaign_id)
        if (any(i in changed_values for i in ["start_date", "end_date", "send_date"])) and len(
            send_complete_msgs
        ) > 0:
            raise PolicyException(
                detail={
                    "code": "send_type/update/denied",
                    "message": "캠페인 메세지가 발송되어 시작일과 종료일을 변경할 수 없습니다.",
                },
            )

        campaign_ids_to_sync = []
        if is_date_values_changed:
            if campaign_req_json["send_type_code"] == SendTypeEnum.RECURRING.value:
                # 주기성 캠페인 정보 갱신
                create_date = datetime.now(selected_timezone)
                # Todo: 추후 주기성에서 시작일자 부여되면 반영
                start_date, end_date = repeat_date.calculate_dates(
                    create_date,
                    period=campaign_req_json["repeat_type"],
                    week_days=campaign_req_json.get("week_days"),
                    datetosend=campaign_req_json.get("datetosend"),
                    timezone=tz,  # timezone
                )
                # retention_day 적용 후 end_date 생성
                retention_day = campaign_req_json.get("retention_day")
                if retention_day:
                    end_date_f = datetime.strptime(end_date, "%Y%m%d")
                    end_date = end_date_f + timedelta(days=int(retention_day))
                    end_date = end_date.strftime("%Y%m%d")

                campaign_ids_to_sync = modify_resv_sync.find_recurring_campaigns()
                campaign_base.group_end_date = campaign_req_json.get("group_end_date")

                # 시작 종료일이 다르면 갱신
                campaign_base.start_date = start_date
                campaign_base.end_date = end_date
                campaign_base.send_date = start_date
                campaign_base.datetosend = campaign_req_json.get("datetosend")
                campaign_base.repeat_type = campaign_req_json.get("repeat_type")
                campaign_base.timetosend = campaign_req_json.get("timetosend")
                campaign_base.week_days = campaign_req_json.get("week_days")
                campaign_base.group_end_date = campaign_req_json.get("group_end_date")
                campaign_base.is_approval_recurred = campaign_req_json.get("is_approval_recurred")
                campaign_base.is_msg_creation_recurred = campaign_req_json.get(
                    "is_msg_creation_recurred"
                )

            else:
                # 일회성에서는 시작일과 종료일 존재
                campaign_base.start_date = campaign_update_obj.start_date
                campaign_base.end_date = campaign_update_obj.end_date
                campaign_base.send_date = campaign_update_obj.send_date
                campaign_base.timetosend = campaign_update_obj.timetosend
                end_date = campaign_update_obj.end_date

            # 발송일이 변경되면 메시지 오브젝트도 변경
            if "send_date" in changed_values:
                set_group_msg_obj = (
                    db.query(SetGroupMessagesEntity)
                    .filter(SetGroupMessagesEntity.campaign_id == campaign_base.campaign_id)
                    .all()
                )
                for msg_obj in set_group_msg_obj:
                    if msg_obj.msg_send_type == "campaign":
                        msg_obj.msg_resv_date = campaign_update_obj.send_date
                        msg_obj.updated_by = str(user_id)

        else:
            end_date = campaign_base.end_date

        # 캠페인 리마인드 체크
        req_remind_update = campaign_req_json.get("remind_list")
        send_type_code = campaign_req_json.get("send_type_code")

        print("send_type_code")
        print(send_type_code)

        remind_dict_list = None
        # remind 정보가 있다면 반드시 End_date가 존재해야함
        if req_remind_update or campaign_base.remind_list:
            remind_dict_list = self.convert_to_campaign_remind(
                user_id, campaign_base.send_date, end_date, req_remind_update, send_type_code
            )
            campaign_base = self.update_remind_obj(db, campaign_base, remind_dict_list)

        db.merge(campaign_base)
        db.flush()

        # 주기성 정보 동기화
        if len(campaign_ids_to_sync) > 0:

            bef_campaign_id = False
            for camp_id in campaign_ids_to_sync:

                # 업데이트해야 할 주기성 캠페인 오브젝트
                recurring_campaign_base = (
                    db.query(CampaignEntity).filter(CampaignEntity.campaign_id == camp_id).first()
                )

                # recurring_campaign_req_obj : 캠페인 base 업데이트
                recurring_campaign_req_obj = modify_resv_sync.sync_recurring_campaign(
                    bef_campaign_id, camp_id, changed_values
                )
                bef_campaign_id = camp_id

                # pydantic모델 ->dictionary
                recurring_campaign_req_json = recurring_campaign_req_obj.json()
                recurring_campaign_req_json = json.loads(recurring_campaign_req_json)

                # 캠페인 리마인드 체크
                recurring_req_remind_update = recurring_campaign_req_json.get("remind_list")
                recurring_send_type_code = recurring_campaign_req_json.get("send_type_code")
                recurring_end_date = recurring_campaign_req_json.get("end_date")

                recurring_remind_dict_list = None
                # remind 정보가 있다면 반드시 End_date가 존재해야함
                if recurring_req_remind_update or recurring_campaign_base.remind_list:
                    recurring_remind_dict_list = self.convert_to_campaign_remind(
                        user_id,
                        campaign_base.send_date,
                        recurring_end_date,
                        recurring_req_remind_update,
                        recurring_send_type_code,
                    )
                    recurring_campaign_base = self.update_remind_obj(
                        db, recurring_campaign_base, recurring_remind_dict_list
                    )

                # TODO
                db.add(recurring_campaign_base)
                db.flush()

        return campaign_base, remind_dict_list

    def convert_to_campaign_remind(self, user_id, send_date, end_date, remind_list, send_type_code):
        """캠페인 리마인드 인서트 딕셔너리 리스트 생성"""

        remind_dict_list = []

        print("remind_list")
        print(remind_list)
        for remind_elem in remind_list:

            """
            remind_step
            remind_duration
            """
            remind_step_dict = {}

            # insert step & duration
            remind_step_dict.update(remind_elem)
            print("remind_step_dict")
            print(remind_step_dict)

            # 리마인드 발송일 계산
            remind_duration = remind_elem["remind_duration"]
            remind_date = calculate_remind_date(end_date, remind_duration)

            if int(remind_date) == int(send_date):
                raise PolicyException(
                    detail={
                        "code": "campaign/remind/date_validation",
                        "message": "리마인드 발송날짜가 캠페인 발송일과 같습니다. 리마인드 시점을 다시 확인해주세요",
                    },
                )
            if int(remind_date) < int(send_date):
                raise PolicyException(
                    detail={
                        "code": "campaign/remind/date_validation",
                        "message": "리마인드 발송날짜가 캠페인 발송일보다 앞에 있습니다. 리마인드 시점을 다시 확인해주세요",
                    },
                )

            remind_step_dict["remind_date"] = remind_date
            remind_step_dict["send_type_code"] = send_type_code
            remind_step_dict["created_by"] = str(user_id)
            remind_step_dict["updated_by"] = str(user_id)

            remind_dict_list.append(remind_step_dict)

        return remind_dict_list

    def update_remind_obj(self, db, campaign_base, remind_dict_list):
        # sort by remind_step
        campaign_base.remind_list.sort(key=lambda x: x.remind_step)
        remind_origin = campaign_base.remind_list
        remind_origin_len = len(remind_origin)
        min_element = min(remind_origin_len, len(remind_dict_list))
        msg_delivery_vendor = campaign_base.msg_delivery_vendor
        campaign_id = campaign_base.campaign_id
        initial_msg_type = {
            CampaignMedia.KAKAO_ALIM_TALK.value: MessageType.KAKAO_ALIM_TEXT.value,
            CampaignMedia.KAKAO_FRIEND_TALK.value: MessageType.KAKAO_IMAGE_GENERAL.value,
            CampaignMedia.TEXT_MESSAGE.value: MessageType.LMS.value,
        }

        # 최소 seq까지 업데이트
        for i in range(min_element):
            steps = i + 1
            origin = [remind for remind in remind_origin if remind.remind_step == steps][0]
            same_step_req_remind = [
                remind for remind in remind_dict_list if remind["remind_step"] == steps
            ][0]
            remind_date_org = origin.remind_date
            remind_media_org = origin.remind_media
            origin.remind_step = same_step_req_remind["remind_step"]
            origin.remind_media = same_step_req_remind["remind_media"]
            origin.remind_duration = same_step_req_remind["remind_duration"]
            origin.remind_date = same_step_req_remind["remind_date"]
            origin.updated_by = same_step_req_remind["updated_by"]

            if remind_date_org != same_step_req_remind["remind_date"]:
                print("remind_date 변경")
                update_query = (
                    update(SetGroupMessagesEntity)
                    .where(
                        and_(
                            SetGroupMessagesEntity.campaign_id == campaign_id,
                            SetGroupMessagesEntity.remind_step == origin.remind_step,
                        )
                    )
                    .values(
                        msg_resv_date=same_step_req_remind["remind_date"],
                        updated_by=same_step_req_remind["updated_by"],
                    )
                )
                db.execute(update_query)

            if remind_media_org != same_step_req_remind["remind_media"]:
                print("remind_media 변경")
                # media가 변경되었다면 메시지 오브젝트도 변경 + msg_body/title/photo_url 초기화
                update_query = (
                    update(SetGroupMessagesEntity)
                    .where(
                        and_(
                            SetGroupMessagesEntity.campaign_id == campaign_id,
                            SetGroupMessagesEntity.remind_step == origin.remind_step,
                        )
                    )
                    .values(
                        media=same_step_req_remind["remind_media"],
                        msg_type=initial_msg_type[same_step_req_remind["remind_media"]],
                        msg_title=None,
                        msg_body=None,
                        msg_photo_uri=None,
                        updated_by=same_step_req_remind["updated_by"],
                    )
                )
                db.execute(update_query)

        # 새로운 리스트가 더 길다면 추가
        if remind_origin_len < len(remind_dict_list):
            set_group_messages_all = []
            for i in range(min_element, len(remind_dict_list)):
                steps = i + 1
                added_remind = [
                    added for added in remind_dict_list if added["remind_step"] == steps
                ][0]

                campaign_base.remind_list.append(CampaignRemindEntity(**added_remind))

                # 추가된 경우 빈 메시지 오브젝트 추가
                get_distinct_set_group_seq = (
                    db.query(
                        SetGroupMessagesEntity.set_group_seq,
                        SetGroupMessagesEntity.set_seq,
                    )
                    .filter(SetGroupMessagesEntity.campaign_id == campaign_id)
                    .distinct()
                    .all()
                )

                for set_group_obj in get_distinct_set_group_seq:
                    set_group_messages = self.create_remind_group_messages(
                        db, added_remind, campaign_id, msg_delivery_vendor, set_group_obj
                    )
                    set_group_messages_all.append(set_group_messages)
            db.bulk_insert_mappings(SetGroupMessagesEntity, set_group_messages_all)

        # 기존 리스트가 더 길다면 삭제
        if remind_origin_len > len(remind_dict_list):
            for i in range(min_element, remind_origin_len):
                steps = i + 1
                # remove object if steps is not in remind_dict_list
                campaign_base.remind_list = [
                    remind for remind in campaign_base.remind_list if remind.remind_step != steps
                ]
                # 삭제된 경우 메시지 오브젝트 삭제
                stmt = delete(CampaignRemindEntity).where(
                    and_(
                        CampaignRemindEntity.remind_step == steps,
                        CampaignRemindEntity.campaign_id == campaign_id,
                    )
                )
                db.execute(stmt)

                # 메시지 삭제
                stmt = delete(SetGroupMessagesEntity).where(
                    and_(
                        SetGroupMessagesEntity.campaign_id == campaign_id,
                        SetGroupMessagesEntity.remind_step == steps,
                    )
                )
                db.execute(stmt)

        return campaign_base

    def create_remind_group_messages(
        self, db, added_remind_dict, campaign_id, msg_delivery_vendor, set_group_obj
    ):
        """캠페인 리마인드 메세지 시퀀스 생성 (set_group_msg_seq)

        *리마인드 메시지에 한해서 set_group_seq별 set_group_msg_seq를 미리 생성
        step1에서 리마인드 변경으로 인해 새로운 리마인드 메시지 생성시 채워짐
          -msg_title
          -msg_body
          -msg_type
          -msg_send_type ..등

        insert tables
        - set_group_messages
        """

        message_sender_info_entity = db.query(MessageIntegrationEntity).first()
        if message_sender_info_entity is None:
            raise PolicyException(detail={"message": "입력된 발신자 정보가 없습니다."})
        bottom_text = f"무료수신거부: {message_sender_info_entity.opt_out_phone_number}"
        phone_callback = message_sender_info_entity.sender_phone_number

        initial_msg_type = {
            CampaignMedia.KAKAO_ALIM_TALK.value: MessageType.KAKAO_ALIM_TEXT.value,
            CampaignMedia.KAKAO_FRIEND_TALK.value: MessageType.KAKAO_IMAGE_GENERAL.value,
            CampaignMedia.TEXT_MESSAGE.value: MessageType.LMS.value,
        }

        set_remind_message_dict = {
            "set_group_seq": set_group_obj.set_group_seq,
            "set_seq": set_group_obj.set_seq,
            "msg_type": initial_msg_type[added_remind_dict["remind_media"]],
            "media": added_remind_dict["remind_media"],
            "bottom_text": bottom_text,
            "phone_callback": phone_callback,
            "campaign_id": campaign_id,
            "msg_send_type": "remind",
            "is_used": True,  # 기본값 True
            "remind_step": added_remind_dict["remind_step"],
            "msg_resv_date": added_remind_dict["remind_date"],
            "created_by": added_remind_dict["updated_by"],
            "updated_by": added_remind_dict["updated_by"],
        }

        return set_remind_message_dict
