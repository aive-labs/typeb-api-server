from datetime import datetime, timedelta

from sqlalchemy.orm import Session

from src.campaign.domain.campaign import Campaign
from src.campaign.domain.campaign_timeline import CampaignTimeline
from src.campaign.enums.campagin_status import CampaignStatus
from src.campaign.enums.campaign_progress import CampaignProgress
from src.campaign.enums.campaign_timeline_type import CampaignTimelineType
from src.campaign.enums.campaign_type import CampaignType
from src.campaign.enums.send_type import SendType, SendTypeEnum
from src.campaign.routes.dto.request.campaign_create import CampaignCreate
from src.campaign.routes.dto.request.campaign_remind import CampaignRemind
from src.campaign.routes.dto.request.campaign_remind_create import CampaignRemindCreate
from src.campaign.routes.dto.response.campaign_basic_response import (
    CampaignBasicResponse,
    RecipientSummary,
)
from src.campaign.routes.port.create_campaign_usecase import CreateCampaignUseCase
from src.campaign.service.port.base_campaign_repository import BaseCampaignRepository
from src.common.timezone_setting import selected_timezone
from src.common.utils.date_utils import calculate_remind_date
from src.common.utils.repeat_date import calculate_dates
from src.core.exceptions.exceptions import (
    DuplicatedException,
    ValidationException,
)
from src.core.transactional import transactional
from src.strategy.service.port.base_strategy_repository import BaseStrategyRepository
from src.users.domain.user import User


class CreateCampaignService(CreateCampaignUseCase):
    def __init__(
        self,
        campaign_repository: BaseCampaignRepository,
        strategy_repository: BaseStrategyRepository,
    ):
        self.campaign_repository = campaign_repository
        self.strategy_repository = strategy_repository

    @transactional
    def create_campaign(self, campaign_create: CampaignCreate, user: User, db: Session):
        # 캠페인명 중복 체크
        is_existing_campaign = self.campaign_repository.is_existing_campaign_by_name(
            campaign_create.campaign_name
        )
        if is_existing_campaign:
            raise DuplicatedException(
                detail={"message": "동일한 캠페인 명이 존재합니다."}
            )

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
                raise ValidationException(
                    detail={"message": "expert 캠페인은 전략을 선택해야 합니다."}
                )

            # TODO 기존 코드인데 audience_type_code에 따른 is_msg_creation_recurred 값 확인 필요
            # if audience_type_code == AudienceType.custom.value:
            #     is_msg_creation_recurred = True
            # else:
            is_msg_creation_recurred = False
        else:
            is_msg_creation_recurred = True

        if campaign_create.repeat_type is None:
            repeat_type = None
        else:
            repeat_type = campaign_create.repeat_type.value

        retention_day = campaign_create.retention_day
        if campaign_create.send_type_code == SendTypeEnum.RECURRING.value:
            created_date = datetime.now(selected_timezone)
            start_date, end_date = calculate_dates(
                start_date=created_date,
                period=campaign_create.repeat_type,
                week_days=campaign_create.week_days,
                datetosend=campaign_create.datetosend,
                timezone="Asia/Seoul",
            )
            if retention_day:
                end_date_f = datetime.strptime(end_date, "%Y%m%d")
                end_date = end_date_f + timedelta(days=int(retention_day))
                end_date = end_date.strftime("%Y%m%d")
        else:
            # 일회성에서는 시작일과 종료일이 존재
            start_date = campaign_create.start_date
            end_date = campaign_create.end_date

        send_type_code = campaign_create.send_type_code
        send_date = (
            campaign_create.send_date if campaign_create.send_date else start_date
        )

        # remind 정보가 있다면 반드시 end_date가 존재해야함
        campaign_remind_list = []
        if campaign_create.remind_list:
            campaign_remind_list = self._convert_to_campaign_remind(
                user.user_id,
                send_date,
                end_date,
                campaign_create.remind_list,
                send_type_code,
            )

        new_campaign = Campaign(
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
            is_msg_creation_recurred=is_msg_creation_recurred,
            start_date=start_date,
            end_date=end_date,
            group_end_date=campaign_create.group_end_date,
            retention_day=retention_day,
            week_days=campaign_create.week_days,
            send_date=send_date,
            is_approval_recurred=campaign_create.is_approval_recurred,
            datetosend=campaign_create.datetosend,
            timetosend=campaign_create.timetosend,
            has_remind=campaign_create.has_remind,
            campaign_theme_ids=campaign_create.strategy_theme_ids,
            is_personalized=campaign_create.is_personalized,
            msg_delivery_vendor=campaign_create.msg_delivery_vendor.value,
            remind_list=campaign_remind_list,
            campaigns_exc=campaign_create.campaigns_exc,
            audiences_exc=campaign_create.audiences_exc,
            created_at=campaign_create.created_at,
            updated_at=campaign_create.updated_at,
        )

        saved_campaign = self.campaign_repository.create_campaign(new_campaign, db)

        # 캠페인 생성 타임라인 추가
        timeline_type = "campaign_event"
        timeline_description = self._get_timeline_description(
            timeline_type=timeline_type,
            created_by_name=user.username,
            description="캠페인 생성",
        )
        # 캠페인 타임라인 테이블 저장
        timeline = CampaignTimeline(
            timeline_type=timeline_type,
            campaign_id=saved_campaign.campaign_id,
            description=timeline_description,
            created_by=str(user.user_id),
            created_by_name=user.username,
        )
        self.campaign_repository.save_timeline(timeline, db)

        if campaign_create.campaign_type_code == CampaignType.expert.value:
            pass
        else:
            recipient_portion = 0
            recipient_descriptions = None
            sets = None
            set_groups = None
            set_group_message_list = None

        return CampaignBasicResponse(
            progress=saved_campaign.progress,
            base=saved_campaign,
            set_summary=RecipientSummary(
                recipient_portion="a", recipient_descriptions="b"
            ),
            set_list=[],
            set_group_list=[],
            set_group_message_list=[],
        )

    def _convert_to_campaign_remind(
        self,
        user_id,
        send_date,
        end_date,
        remind_create_list: list[CampaignRemindCreate],
        send_type_code,
    ):
        """캠페인 리마인드 인서트 딕셔너리 리스트 생성"""

        campaign_remind_list = []
        for remind_create in remind_create_list:
            # 리마인드 발송일 계산
            remind_duration = remind_create.remind_duration
            remind_date = calculate_remind_date(end_date, remind_duration)

            if int(remind_date) == int(send_date):
                raise ValidationException(
                    detail={
                        "code": "campaign/remind/date_validation",
                        "message": "리마인드 발송날짜가 캠페인 발송일과 같습니다. 리마인드 시점을 다시 확인해주세요",
                    },
                )
            if int(remind_date) < int(send_date):
                raise ValidationException(
                    detail={
                        "code": "campaign/remind/date_validation",
                        "message": "리마인드 발송날짜가 캠페인 발송일보다 앞에 있습니다. 리마인드 시점을 다시 확인해주세요",
                    },
                )

            campaign_remind_list.append(
                CampaignRemind(
                    send_type_code=send_type_code,
                    remind_step=remind_create.remind_step,
                    remind_duration=remind_create.remind_duration,
                    remind_media=(
                        remind_create.remind_media.value
                        if remind_create.remind_media
                        else None
                    ),
                    remind_date=remind_date,
                    created_by=str(user_id),
                    updated_by=str(user_id),
                )
            )

        return campaign_remind_list

    def _get_timeline_description(
        self,
        timeline_type,
        created_by_name,
        to_status=None,
        description=None,
        approval_excute=False,
    ) -> str | None:

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
                raise ValidationException(detail={"message": "Invalid campagin status"})
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
            raise ValidationException(detail={"message": "Invalid campagin status"})

        return description
