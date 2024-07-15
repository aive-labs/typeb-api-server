from collections import defaultdict
from datetime import datetime, timedelta

import pandas as pd
from sqlalchemy.orm import Session

from src.campaign.domain.campaign import Campaign
from src.campaign.domain.campaign_remind import CampaignRemind
from src.campaign.domain.campaign_timeline import CampaignTimeline
from src.campaign.enums.campagin_status import CampaignStatus
from src.campaign.enums.campaign_progress import CampaignProgress
from src.campaign.enums.campaign_timeline_type import CampaignTimelineType
from src.campaign.enums.campaign_type import CampaignType
from src.campaign.enums.send_type import SendType, SendTypeEnum
from src.campaign.infra.sqlalchemy_query.get_campaign_set_groups import (
    get_campaign_set_groups,
)
from src.campaign.infra.sqlalchemy_query.get_campaign_sets import get_campaign_sets
from src.campaign.infra.sqlalchemy_query.get_set_rep_nm_list import get_set_rep_nm_list
from src.campaign.routes.dto.request.campaign_create import CampaignCreate
from src.campaign.routes.dto.request.campaign_remind_create import CampaignRemindCreate
from src.campaign.routes.dto.response.campaign_basic_response import (
    CampaignBasicResponse,
    RecipientSummary,
)
from src.campaign.routes.port.create_campaign_usecase import CreateCampaignUseCase
from src.campaign.service.campaign_dependency_manager import CampaignDependencyManager
from src.campaign.service.port.base_campaign_repository import BaseCampaignRepository
from src.campaign.service.port.base_campaign_set_repository import (
    BaseCampaignSetRepository,
)
from src.campaign.utils.utils import set_summary_sententce
from src.common.timezone_setting import selected_timezone
from src.common.utils.data_converter import DataConverter
from src.common.utils.date_utils import calculate_remind_date
from src.common.utils.repeat_date import calculate_dates
from src.core.exceptions.exceptions import (
    ConsistencyException,
    DuplicatedException,
    ValidationException,
)
from src.core.transactional import transactional
from src.strategy.enums.recommend_model import RecommendModels
from src.strategy.service.port.base_strategy_repository import BaseStrategyRepository
from src.users.domain.user import User


class CreateCampaignService(CreateCampaignUseCase):
    def __init__(
        self,
        campaign_repository: BaseCampaignRepository,
        strategy_repository: BaseStrategyRepository,
        campaign_set_repository: BaseCampaignSetRepository,
    ):
        self.campaign_repository = campaign_repository
        self.strategy_repository = strategy_repository
        self.campaign_set_repository = campaign_set_repository

    @transactional
    def create_campaign(
        self, campaign_create: CampaignCreate, user: User, db: Session
    ) -> CampaignBasicResponse:
        # 캠페인명 중복 체크
        is_existing_campaign = self.campaign_repository.is_existing_campaign_by_name(
            campaign_create.campaign_name
        )
        if is_existing_campaign:
            raise DuplicatedException(detail={"message": "동일한 캠페인 명이 존재합니다."})

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
        send_date = campaign_create.send_date if campaign_create.send_date else start_date

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
            campaign_type_name=CampaignType.get_name(campaign_create.campaign_type_code.value),
            campaign_status_group_code=CampaignStatus.tempsave.group,
            campaign_status_group_name=CampaignStatus.tempsave.group_description,
            campaign_status_code=CampaignStatus.tempsave.value,
            campaign_status_name=CampaignStatus.tempsave.description,
            send_type_code=campaign_create.send_type_code.value,
            send_type_name=SendType.get_name(campaign_create.send_type_code.value),
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
            strategy_theme_ids=campaign_create.strategy_theme_ids,
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
            campaign_id = saved_campaign.campaign_id
            if not campaign_id:
                raise ConsistencyException(detail={"message": "캠페인의 id가 발급되지 않았습니다."})

            self.create_campaign_set(saved_campaign, user, db)
            sets = [row._asdict() for row in get_campaign_sets(campaign_id=campaign_id, db=db)]
            set_groups = [
                row._asdict() for row in get_campaign_set_groups(campaign_id=campaign_id, db=db)
            ]

            sets = self.add_set_rep_contents(sets, set_groups, campaign_id, db)
            set_group_messages = self.campaign_set_repository.get_campaign_set_group_messages(
                campaign_id=campaign_id, db=db
            )
            set_group_message_list = self.convert_to_set_group_message_list(set_group_messages)

            recipient_portion, _, set_cus_count = self.campaign_set_repository.get_set_portion(
                campaign_id, db
            )
            set_df = pd.DataFrame(sets)

            recipient_descriptions = set_summary_sententce(set_cus_count, set_df)
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
                recipient_portion=recipient_portion, recipient_descriptions=recipient_descriptions
            ),
            set_list=sets,
            set_group_list=set_groups,
            set_group_message_list=set_group_message_list,
        )

    def create_campaign_set(self, saved_campaign: Campaign, user: User, db: Session):
        selected_themes, campaign_theme_ids = self.campaign_set_repository.create_campaign_set(
            saved_campaign, str(user.user_id), db
        )

        campaign_type_code = saved_campaign.campaign_type_code
        strategy_id = saved_campaign.strategy_id
        campaign_id = saved_campaign.campaign_id

        # expert 캠페인일 경우 데이터 sync 진행
        campaign_dependency_manager = CampaignDependencyManager(user)

        if campaign_type_code == CampaignType.expert.value:
            campaign_dependency_manager.sync_campaign_base(
                db, campaign_id, selected_themes, campaign_theme_ids
            )
            campaign_dependency_manager.sync_strategy_status(db, strategy_id)
        campaign_dependency_manager.sync_audience_status(db, campaign_id)

        db.flush()

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
                    send_type_code=send_type_code.value,
                    remind_step=remind_create.remind_step,
                    remind_duration=remind_create.remind_duration,
                    remind_media=(
                        remind_create.remind_media.value if remind_create.remind_media else None
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

    def add_set_rep_contents(self, sets, set_groups, campaign_id, db):
        recsys_model_enum_dict = RecommendModels.get_eums()
        personalized_recsys_model_id = [
            i["_value_"] for i in recsys_model_enum_dict if i["personalized"] is True
        ]
        personalized_recsys_model_id.remove(RecommendModels.new_collection_rec.value)
        not_personalized_set = []

        for idx, row in enumerate(sets):
            # row is dict
            recsys_model_id = row.get("recsys_model_id")
            recsys_model_id = int(float(recsys_model_id)) if recsys_model_id else None
            set_sort_num = row["set_sort_num"]

            if recsys_model_id in personalized_recsys_model_id:
                sets[idx]["rep_nm_list"] = ["개인화"]
                sets[idx]["contents_names"] = ["개인화"]
            else:
                sets[idx]["rep_nm_list"] = None
                sets[idx]["contents_names"] = None
                not_personalized_set.append(set_sort_num)
        # rep_nm_list
        query = get_set_rep_nm_list(
            campaign_id=campaign_id, set_sort_num_list=not_personalized_set, db=db
        )
        recipients = DataConverter.convert_query_to_df(query)
        sort_num_dict = (
            recipients.set_index("set_sort_num")["rep_nm_list"]
            .apply(lambda x: x if x != [None] else [])
            .to_dict()
        )
        for idx, set_dict in enumerate(sets):
            for set_sort_num in sort_num_dict:
                if set_dict["set_sort_num"] == set_sort_num:
                    sets[idx]["rep_nm_list"] = sort_num_dict[set_sort_num]
        # contents_names
        result_dict = {}
        for item in set_groups:
            key = item["set_sort_num"]
            value = item["contents_name"]

            if key in result_dict and value is not None:
                result_dict[key].append(value)
            else:
                result_dict[key] = [] if value is None else [value]

        for idx, set_dict in enumerate(sets):
            for set_sort_num in result_dict:
                if set_dict["set_sort_num"] == set_sort_num:
                    # 콘텐츠명 중복 제거
                    sets[idx]["contents_names"] = list(set(result_dict[set_sort_num]))
        return sets

    def convert_to_set_group_message_list(self, set_group_messages):

        result_dict = defaultdict(list)
        # {set_seq: dict()}
        for item in set_group_messages:
            set_seq = item["set_seq"]
            result_dict[set_seq].append(item)

        result_dict = dict(result_dict)

        for k, _ in result_dict.items():
            # k -> set_seq
            set_group_list = result_dict[k]
            total_list = []
            for g_idx, _ in enumerate(set_group_list):
                # g_idx -> set_group index
                set_group_messages = result_dict[k][g_idx].copy()

                if len(total_list) == 0:
                    sub_dict = {}
                    sub_dict["set_group_seq"] = set_group_messages["set_group_seq"]
                    sub_dict["group_sort_num"] = set_group_messages["group_sort_num"]
                    sub_dict["set_seq"] = set_group_messages["set_seq"]
                    set_group_messages.pop("set_group_seq")
                    sub_dict["campaign_msg"] = (
                        set_group_messages
                        if set_group_messages["msg_send_type"] == "campaign"
                        else None
                    )

                    if sub_dict["campaign_msg"]:
                        sub_dict["campaign_msg"]["rec_explanation"] = set_group_messages[
                            "rec_explanation"
                        ]

                    sub_dict["remind_msg_list"] = (
                        [set_group_messages]
                        if set_group_messages["msg_send_type"] == "remind"
                        else None
                    )

                    if sub_dict["remind_msg_list"]:
                        for i, _ in enumerate(sub_dict["remind_msg_list"]):
                            sub_dict["remind_msg_list"][i]["remind_seq"] = set_group_messages[
                                "remind_seq"
                            ]

                    total_list.append(sub_dict)

                else:
                    # total_list에 이미 있는 set_group_seq를 제외한 set_group_seq 리스트
                    set_group_seqs = list({elem_dict["set_group_seq"] for elem_dict in total_list})

                    if set_group_messages["set_group_seq"] not in set_group_seqs:
                        sub_dict = {}
                        sub_dict["set_group_seq"] = set_group_messages["set_group_seq"]
                        sub_dict["group_sort_num"] = set_group_messages["group_sort_num"]
                        sub_dict["set_seq"] = set_group_messages["set_seq"]
                        set_group_messages.pop("set_group_seq")

                        sub_dict["campaign_msg"] = (
                            set_group_messages
                            if set_group_messages["msg_send_type"] == "campaign"
                            else None
                        )

                        if sub_dict["campaign_msg"]:
                            sub_dict["campaign_msg"]["rec_explanation"] = set_group_messages[
                                "rec_explanation"
                            ]

                        sub_dict["remind_msg_list"] = (
                            [set_group_messages]
                            if set_group_messages["msg_send_type"] == "remind"
                            else None
                        )

                        if sub_dict["remind_msg_list"]:
                            for i, _ in enumerate(sub_dict["remind_msg_list"]):
                                sub_dict["remind_msg_list"][i]["remind_seq"] = set_group_messages[
                                    "remind_seq"
                                ]

                        total_list.append(sub_dict)

                    else:
                        # total_list에 이미 있는 set_group_seq가 있는 경우 append

                        total_list_index = None
                        for idx, elem_dict in enumerate(total_list):

                            if elem_dict["set_group_seq"] == set_group_messages["set_group_seq"]:
                                total_list_index = idx

                        set_group_messages.pop("set_group_seq")

                        # 리마인드 메세지가 들어온 경우
                        if set_group_messages["msg_send_type"] == "remind":

                            if total_list[total_list_index]["remind_msg_list"]:
                                # 리마인드 메세지가 1개 이상 들어와 있는 경우
                                total_list[total_list_index]["remind_msg_list"].append(
                                    set_group_messages
                                )
                            else:
                                # 리마인드 메세지가 새로 들어오는 경우
                                total_list[total_list_index]["remind_msg_list"] = [
                                    set_group_messages
                                ]

                        # 캠페인 메세지가 들어온 경우
                        elif set_group_messages["msg_send_type"] == "campaign":
                            total_list[total_list_index]["campaign_msg"] = set_group_messages

            # 1개 set_seq에 대한 group_message 할당 완료
            result_dict[k] = total_list

        return result_dict
