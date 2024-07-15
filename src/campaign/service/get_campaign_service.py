from collections import defaultdict

import pandas as pd
from sqlalchemy.orm import Session

from src.campaign.domain.campaign import Campaign
from src.campaign.enums.campaign_type import CampaignType
from src.campaign.infra.sqlalchemy_query.get_campaign_set_groups import (
    get_campaign_set_groups,
)
from src.campaign.infra.sqlalchemy_query.get_campaign_sets import get_campaign_sets
from src.campaign.infra.sqlalchemy_query.get_set_rep_nm_list import get_set_rep_nm_list
from src.campaign.routes.dto.response.campaign_basic_response import (
    CampaignBasicResponse,
    RecipientSummary,
)
from src.campaign.routes.dto.response.campaign_response import CampaignSet
from src.campaign.routes.dto.response.campaign_reviewer import CampaignReviewer
from src.campaign.routes.dto.response.campaign_timeline_response import (
    CampaignTimelineResponse,
    StatusUserProfile,
)
from src.campaign.routes.port.get_campaign_usecase import GetCampaignUseCase
from src.campaign.service.port.base_campaign_repository import BaseCampaignRepository
from src.campaign.service.port.base_campaign_set_repository import (
    BaseCampaignSetRepository,
)
from src.campaign.utils.utils import set_summary_sententce
from src.common.utils.data_converter import DataConverter
from src.strategy.enums.recommend_model import RecommendModels
from src.users.domain.user import User


class GetCampaignService(GetCampaignUseCase):

    def __init__(
        self,
        campaign_repository: BaseCampaignRepository,
        campaign_set_repository: BaseCampaignSetRepository,
    ):
        self.campaign_repository = campaign_repository
        self.campaign_set_repository = campaign_set_repository

    def get_campaigns(self, start_date: str, end_date: str, user: User) -> list[Campaign]:
        campaigns = self.campaign_repository.get_campaigns(start_date, end_date, user)
        return campaigns

    def get_timeline(self, campaign_id: str, db: Session) -> list[CampaignTimelineResponse]:
        campaign_timelines = self.campaign_repository.get_timeline(campaign_id, db)

        return [
            CampaignTimelineResponse(
                timeline_no=timeline.timeline_no,
                timeline_type=timeline.timeline_type,
                description=timeline.description,
                status_no=timeline.status_no,
                created_at=timeline.created_at,
                created_by=StatusUserProfile(
                    user_id=timeline.created_by,
                    username=timeline.created_by_name,
                    email=timeline.email,
                    photo_uri=timeline.photo_uri,
                    department_id=timeline.department_id,
                    department_name=timeline.department_name,
                    test_callback_number=timeline.test_callback_number,
                ),
            )
            for timeline in campaign_timelines
        ]

    def get_campaign_detail(self, campaign_id, user, db: Session) -> CampaignBasicResponse:
        campaign = self.campaign_repository.get_campaign_detail(campaign_id, user, db)
        campaign_reminds = self.campaign_repository.get_campaign_remind(campaign_id, db)

        # remind_list = [
        #     CampaignRemindResponse(
        #         remind_step=remind.remind_step,
        #         remind_media=remind.remind_media,
        #         remind_duration=remind.remind_duration,
        #     )
        #     for remind in campaign_reminds
        # ]
        campaign.remind_list = campaign_reminds

        sets = [row._asdict() for row in get_campaign_sets(campaign_id=campaign_id, db=db)]
        set_groups = [
            row._asdict() for row in get_campaign_set_groups(campaign_id=campaign_id, db=db)
        ]

        # rep_nm_list & contents_names
        if campaign.campaign_type_code == CampaignType.expert.value:
            sets = self.add_set_rep_contents(sets, set_groups, campaign_id, db=db)
        else:
            sets = [
                {**data_dict, "rep_nm_list": None, "contents_names": None} for data_dict in sets
            ]

        campaign_sets = [
            CampaignSet(
                set_seq=campaign_set["set_seq"],
                set_sort_num=campaign_set["set_sort_num"],
                is_group_added=campaign_set["is_group_added"],
                campaign_theme_id=campaign_set["campaign_theme_id"],
                campaign_theme_name=campaign_set["campaign_theme_name"],
                recsys_model_id=campaign_set["recsys_model_id"],
                audience_id=campaign_set["audience_id"],
                audience_name=campaign_set["audience_name"],
                audience_count=campaign_set["audience_count"],
                audience_portion=campaign_set["audience_portion"],
                audience_unit_price=campaign_set["audience_unit_price"],
                response_rate=campaign_set["response_rate"],
                rep_nm_list=campaign_set["rep_nm_list"],
                coupon_no=campaign_set["coupon_no"],
                coupon_name=campaign_set["coupon_name"],
                recipient_count=campaign_set["recipient_count"],
                medias=campaign_set["medias"],
                contents_names=campaign_set["contents_names"],
                is_confirmed=campaign_set["is_confirmed"],
                is_message_confirmed=campaign_set["is_message_confirmed"],
                media_cost=campaign_set["media_cost"],
            )
            for campaign_set in sets
        ]

        set_group_messages = self.campaign_set_repository.get_campaign_set_group_messages(
            campaign_id=campaign_id, db=db
        )

        set_group_message_list = self.convert_to_set_group_message_list(set_group_messages)

        recipient_portion, total_cus, set_cus_count = self.campaign_set_repository.get_set_portion(
            campaign_id, db
        )
        set_df = pd.DataFrame(sets)

        if len(set_df) > 0:
            recipient_descriptions = set_summary_sententce(set_cus_count, set_df)
        else:
            recipient_descriptions = None

        reviewer_list = self.campaign_repository.get_campaign_reviewers(campaign_id, db)
        for reviewer in reviewer_list:
            reviewer.user_name = "/".join([reviewer.user_name, reviewer.department_abb_name])

        return CampaignBasicResponse(
            progress=campaign.progress,
            base=campaign,
            set_summary=RecipientSummary(
                recipient_portion=recipient_portion, recipient_descriptions=recipient_descriptions
            ),
            set_list=campaign_sets,
            set_group_list=set_groups,
            set_group_message_list=set_group_message_list,
            reviewers=[
                CampaignReviewer(
                    approval_no=reviewer.approval_no,
                    user_id=int(reviewer.user_id),
                    user_name_object=reviewer.user_name,
                    test_callback_number=reviewer.test_callback_number,
                    is_approved=reviewer.is_approved,
                )
                for reviewer in reviewer_list
            ],
        )

    def add_set_rep_contents(self, sets, set_groups, campaign_id, db: Session):
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
