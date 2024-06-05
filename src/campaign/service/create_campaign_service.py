from datetime import datetime, timedelta

from fastapi import HTTPException

from src.audiences.enums.audience_type import AudienceType
from src.campaign.domain.campaign import Campaign
from src.campaign.enums.campagin_status import CampaignStatus
from src.campaign.enums.campaign_progress import CampaignProgress
from src.campaign.enums.campaign_type import CampaignType
from src.campaign.enums.send_type import SendType, SendtypeEnum
from src.campaign.routes.dto.request.campaign_create import CampaignCreate
from src.campaign.routes.dto.request.campaign_remind import CampaignRemind
from src.campaign.routes.port.create_campaign_usecase import CreateCampaignUsecase
from src.campaign.service.port.base_campaign_repository import BaseCampaignRepository
from src.common.timezone_setting import selected_timezone
from src.core.exceptions import DuplicatedError
from src.strategy.service.port.base_strategy_repository import BaseStrategyRepository
from src.users.domain.user import User
from src.utils.date_utils import calculate_remind_date, localtime_converter
from src.utils.repeat_date import calculate_dates


class CreateCampaignService(CreateCampaignUsecase):

    def __init__(
        self,
        campaign_repository: BaseCampaignRepository,
        strategy_repository: BaseStrategyRepository,
    ):
        self.campaign_repository = campaign_repository
        self.strategy_repository = strategy_repository

    def create_campaign(self, campaign_create: CampaignCreate, user: User):
        # 캠페인명 중복 체크
        is_existing_campaign = self.campaign_repository.is_existing_campaign_by_name(
            campaign_create.campaign_name
        )
        if is_existing_campaign:
            raise DuplicatedError("동일한 캠페인 명이 존재합니다.")

        if user.user_id is None:
            raise Exception("user_id는 none일 수 없습니다.")

        if user.department_id is None:
            raise Exception("department_id은 none일 수 없습니다.")

        if user.department_name is None:
            raise Exception("department_name은 none일 수 없습니다.")

        if user.role_id == "branch_user":
            shop_send_yn = "y"
        else:
            shop_send_yn = "n"

        if campaign_create.campaign_type_code == CampaignType.expert.value:
            strategy_id = campaign_create.strategy_id

            if strategy_id is None:
                raise Exception("전략 id가 존재하지 않습니다.")

            strategy = self.strategy_repository.find_by_strategy_id(strategy_id)
            audience_type_code = strategy.audience_type_code

            if audience_type_code == AudienceType.custom.value:
                is_msg_creation_recurred = True
            else:
                is_msg_creation_recurred = False
        else:
            audience_type_code = AudienceType.custom.value
            is_msg_creation_recurred = True

        if campaign_create.repeat_type is None:
            repeat_type = None
        else:
            repeat_type = campaign_create.repeat_type.value

        if campaign_create.send_type_code == SendtypeEnum.RECURRING.value:

            created_date = datetime.now(selected_timezone)
            start_date, end_date = calculate_dates(
                start_date=created_date,
                period=campaign_create.repeat_type,
                week_days=campaign_create.week_days,
                datetosend=campaign_create.datetosend,
                timezone="Asia/Seoul",
            )

            retention_day = campaign_create.retention_day
            if retention_day:
                end_date_f = datetime.strptime(end_date, "%Y%m%d")
                end_date = end_date_f + timedelta(days=int(retention_day))
                end_date = end_date.strftime("%Y%m%d")

        else:
            end_date = campaign_create.end_date

        remind_list = campaign_create.remind_list

        send_type_code = campaign_create.send_type_code
        send_date = (
            campaign_create.send_date if campaign_create.send_date else start_date
        )

        if remind_list:
            remind_dict_list = self._convert_to_campaign_remind(
                user.user_id, send_date, end_date, remind_list, send_type_code
            )
            [
                CampaignRemind(**remind_dict) for remind_dict in remind_dict_list
            ]

        Campaign(
            # from reqeust model
            campaign_name=campaign_create.campaign_name,
            campaign_group_id=None,
            budget=campaign_create.budget,
            campaign_type_code=campaign_create.campaign_type_code.value,
            medias=campaign_create.medias,
            campaign_type_name=CampaignType.get_name(
                campaign_create.campaign_type_code
            ),
            campaign_status_group_code=CampaignStatus.tempsave.group,
            campaign_status_group_name=CampaignStatus.tempsave.group_description,
            campaign_status_code=CampaignStatus.tempsave.value,
            campaign_status_name=CampaignStatus.tempsave.description,
            send_type_code=campaign_create.send_type_code.value,
            send_type_name=SendType.get_name(campaign_create.send_type_code),
            progress=CampaignProgress.base_complete.value,
            repeat_type=repeat_type,
            # from user info
            created_by=str(user.user_id),
            updated_by=str(user.user_id),
            owned_by_dept=user.department_id,
            owned_by_dept_name=user.department_name,
            owned_by_dept_abb_name=user.department_name,
            created_by_name=user.username,
            shop_send_yn=shop_send_yn,
            # from logic
            strategy_id=campaign_create.strategy_id,
            audience_type_code=audience_type_code,
            is_msg_creation_recurred=is_msg_creation_recurred,
            start_date=start_date,
            end_date=end_date,
            group_end_date=campaign_create.group_end_date,
            retention_day=str(retention_day),
            week_days=campaign_create.week_days,
            send_date=send_date,
            is_approval_recurred=campaign_create.is_approval_recurred,
            datetosend=campaign_create.datetosend,
            timetosend=campaign_create.timetosend,
            has_remind=campaign_create.has_remind,
            campaign_theme_ids=campaign_create.campaign_theme_ids,
            is_personalized=campaign_create.is_personalized,
            msg_delivery_vendor=campaign_create.msg_delivery_vendor.value,
            campaigns_exc=campaign_create.campaigns_exc,
            audiences_exc=campaign_create.audiences_exc,
            created_at=campaign_create.created_at,
            updated_at=campaign_create.updated_at,
        )

        self.campaign_repository.create_campaign()

        # TODO: 생성 타임 로그

        # TODO: 캠페인 오브젝트 리턴

    def _convert_to_campaign_remind(
        self, user_id, send_date, end_date, remind_list, send_type_code
    ):
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
