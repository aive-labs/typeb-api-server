from collections import defaultdict

import pandas as pd
from sqlalchemy.orm import Session

from src.campaign.domain.campaign import Campaign
from src.campaign.enums.campaign_type import CampaignType
from src.campaign.infra.sqlalchemy_query.add_set_rep_contents import (
    add_set_rep_contents,
)
from src.campaign.infra.sqlalchemy_query.get_audience_rank_between import (
    get_audience_rank_between,
)
from src.campaign.infra.sqlalchemy_query.get_campaign_set_groups import (
    get_campaign_set_groups,
)
from src.campaign.infra.sqlalchemy_query.get_campaign_sets import get_campaign_sets
from src.campaign.infra.sqlalchemy_query.get_customer_by_audience_id import (
    get_customers_by_audience_id,
)
from src.campaign.infra.sqlalchemy_query.get_customer_by_excluded_audience_id import (
    get_customer_by_excluded_audience_ids,
)
from src.campaign.infra.sqlalchemy_query.get_excluded_customer_list_for_calculation import (
    get_excluded_customer_list_for_calculation,
)
from src.campaign.infra.sqlalchemy_query.get_strategy_theme_audience_mapping import (
    get_strategy_theme_audience_mapping_query,
)
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
from src.campaign.routes.dto.response.exclusion_customer_detail import (
    ExcludeCustomerDetail,
    ExcludeCustomerDetailStats,
)
from src.campaign.routes.port.get_campaign_usecase import GetCampaignUseCase
from src.campaign.service.campaign_manager import CampaignManager
from src.campaign.service.port.base_campaign_repository import BaseCampaignRepository
from src.campaign.service.port.base_campaign_set_repository import (
    BaseCampaignSetRepository,
)
from src.campaign.utils.utils import set_summary_sentence
from src.common.enums.campaign_media import CampaignMedia
from src.common.utils.data_converter import DataConverter
from src.core.exceptions.exceptions import PolicyException
from src.message_template.enums.message_type import MessageType
from src.users.domain.user import User


class GetCampaignService(GetCampaignUseCase):

    def __init__(
        self,
        campaign_repository: BaseCampaignRepository,
        campaign_set_repository: BaseCampaignSetRepository,
    ):
        self.campaign_repository = campaign_repository
        self.campaign_set_repository = campaign_set_repository

    def get_campaigns(
        self, start_date: str, end_date: str, user: User, db: Session
    ) -> list[Campaign]:
        campaigns = self.campaign_repository.get_campaigns(start_date, end_date, user, db)
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
        campaign.remind_list = campaign_reminds

        sets = [row._asdict() for row in get_campaign_sets(campaign_id=campaign_id, db=db)]
        set_groups = [
            row._asdict() for row in get_campaign_set_groups(campaign_id=campaign_id, db=db)
        ]

        # rep_nm_list & contents_names
        if campaign.campaign_type_code == CampaignType.EXPERT.value:
            sets = add_set_rep_contents(sets, set_groups, campaign_id, db=db)

        else:
            sets = [
                {**data_dict, "rep_nm_list": None, "contents_names": None} for data_dict in sets
            ]

        campaign_sets = [
            CampaignSet(
                set_seq=campaign_set["set_seq"],
                set_sort_num=campaign_set["set_sort_num"],
                is_group_added=campaign_set["is_group_added"],
                strategy_theme_id=campaign_set["strategy_theme_id"],
                strategy_theme_name=campaign_set["strategy_theme_name"],
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
            recipient_descriptions = set_summary_sentence(set_cus_count, set_df)
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

    def get_exclude_customer(
        self, campaign_id: str, user: User, db: Session
    ) -> ExcludeCustomerDetail:
        campaign = self.campaign_repository.get_campaign_detail(campaign_id, user, db)
        shop_send_yn = campaign.shop_send_yn

        campaign_manager = CampaignManager(db, shop_send_yn, user.user_id)

        media = "tms" if "tms" in campaign.medias.split(",") else campaign.medias.split(",")[-1]

        campaign_type_code = campaign.campaign_type_code
        selected_themes = campaign.strategy_theme_ids
        campaigns_exc = campaign.campaigns_exc
        audiences_exc = campaign.audiences_exc

        initial_msg_type = {
            CampaignMedia.KAKAO_ALIM_TALK.value: MessageType.KAKAO_ALIM_TEXT.value,
            CampaignMedia.KAKAO_FRIEND_TALK.value: MessageType.KAKAO_IMAGE_GENERAL.value,
            CampaignMedia.TEXT_MESSAGE.value: MessageType.LMS.value,
        }

        budget_list = [(media, initial_msg_type[media])]
        remind_data = self.campaign_repository.get_campaign_remind(campaign_id, db)
        for remind in remind_data:
            if remind.remind_media:
                budget_list.append((remind.remind_media, initial_msg_type[remind.remind_media]))

        limit_count = None

        # 테마정보
        if campaign_type_code == CampaignType.EXPERT.value:
            themes_query = get_strategy_theme_audience_mapping_query(selected_themes, db)
            themes_df = DataConverter.convert_query_to_df(themes_query)
        else:
            campaign_manager._load_campaign_object(campaign.model_dump())
            themes_df = campaign_manager.campaign_set_df

        audience_ids = list(set(themes_df["audience_id"]))
        sets_data = get_campaign_sets(campaign_id, db)
        sets_df = DataConverter.convert_query_to_df(sets_data)

        cust_audiences = get_customers_by_audience_id(audience_ids, db)
        cust_audiences_df = DataConverter.convert_query_to_df(cust_audiences)
        if campaign_type_code == CampaignType.EXPERT.value:
            audience_rank_between = get_audience_rank_between(audience_ids, db)
            audience_rank_between_df = DataConverter.convert_query_to_df(audience_rank_between)
            themes_df = pd.merge(themes_df, audience_rank_between_df, on="audience_id", how="inner")
            themes_df = themes_df.loc[themes_df.groupby(["audience_id"])["rank"].idxmin()]
            themes_df["set_sort_num"] = range(1, len(themes_df) + 1)

        campaign_set_df_merged = cust_audiences_df.merge(themes_df, on="audience_id", how="inner")
        campaign_set_df = campaign_set_df_merged.loc[
            campaign_set_df_merged.groupby(["cus_cd"])["set_sort_num"].idxmin()
        ]
        campaign_set_df = pd.merge(
            campaign_set_df,
            sets_df[["audience_id"]].drop_duplicates(),
            on=["audience_id"],
            how="inner",
        )
        del campaign_set_df_merged

        if len(campaign_set_df) == 0:
            raise PolicyException(
                detail={
                    "code": "campaign/excluded-custs/get",
                    "message": "적합한 고객이 존재하지 않습니다.",
                },
            )

        # 대상 고객
        org_campaign_set_df = campaign_set_df[["cus_cd"]].drop_duplicates()
        tot_custs = len(org_campaign_set_df)
        summary_df = pd.DataFrame()

        # 제외 캠페인 고객 필터
        if campaigns_exc:
            exc_campaign_cust = get_excluded_customer_list_for_calculation(campaigns_exc, db)
            exc_campaign_cust_df_raw = DataConverter.convert_query_to_df(exc_campaign_cust).rename(
                columns={"exc_cus_cd": "cus_cd"}
            )
            exc_campaign_cust_df = pd.merge(
                exc_campaign_cust_df_raw, org_campaign_set_df, on="cus_cd", how="inner"
            )
            exclusion_campaign_df = exc_campaign_cust_df.groupby(
                ["campaign_id", "campaign_name"]
            ).size()

            # 제외 캠페인 전처리
            camp_id_with_name = exc_campaign_cust_df_raw[
                ["campaign_id", "campaign_name"]
            ].drop_duplicates()
            exclusion_campaign_df = (
                exclusion_campaign_df.reindex(  # pyright: ignore [reportCallIssue]
                    camp_id_with_name, fill_value=0
                ).reset_index(name="count")
            )
            exclusion_campaign_df["div"] = "캠페인"
            exclusion_campaign_df.columns = ["id", "name", "count", "div"]
            exclusion_campaign_df = exclusion_campaign_df[["div", "id", "name", "count"]]
            summary_df = pd.concat([summary_df, exclusion_campaign_df])

            ## 중복 제거
            exc_cus_df = exc_campaign_cust_df[["cus_cd"]].drop_duplicates()
            campaign_set_df = pd.merge(
                campaign_set_df, exc_cus_df, on="cus_cd", how="left", indicator=True
            )
            campaign_set_df = campaign_set_df[campaign_set_df["_merge"] == "left_only"].drop(
                columns=["_merge"]
            )
        else:
            exclusion_campaign_df = pd.DataFrame(
                {"div": ["캠페인"], "id": [""], "name": [""], "count": [0]}
            )

        if audiences_exc:
            exc_audience_cust = get_customer_by_excluded_audience_ids(audiences_exc, db)
            exc_audience_cust_df_raw = DataConverter.convert_query_to_df(exc_audience_cust).rename(
                columns={"exc_cus_cd": "cus_cd"}
            )
            exc_audience_cust_df = pd.merge(
                exc_audience_cust_df_raw, org_campaign_set_df, on="cus_cd", how="inner"
            )
            exclusion_audience_df = exc_audience_cust_df.groupby(
                ["audience_id", "audience_name"]
            ).size()

            # 제외 오디언스 전처리
            aud_id_with_name = exc_audience_cust_df_raw[
                ["audience_id", "audience_name"]
            ].drop_duplicates()
            exclusion_audience_df = (
                exclusion_audience_df.reindex(  # pyright: ignore [reportCallIssue]
                    aud_id_with_name, fill_value=0
                ).reset_index(name="count")
            )
            exclusion_audience_df["div"] = "타겟 오디언스"
            exclusion_audience_df.columns = ["id", "name", "count", "div"]
            exclusion_audience_df = exclusion_audience_df[["div", "id", "name", "count"]]
            summary_df = pd.concat([summary_df, exclusion_audience_df])

            ## 중복 제거
            exc_aud_df = exc_audience_cust_df[["cus_cd"]].drop_duplicates()
            campaign_set_df = pd.merge(
                campaign_set_df, exc_aud_df, on="cus_cd", how="left", indicator=True
            )
            campaign_set_df = campaign_set_df[campaign_set_df["_merge"] == "left_only"].drop(
                columns=["_merge"]
            )
        else:
            exclusion_audience_df = pd.DataFrame(
                {"div": ["타겟 오디언스"], "id": [""], "name": [""], "count": [0]}
            )

        ## 예산 적용, 커스텀에서는 고객을 가져올때 ltv가 없으므로 포함
        cust_after_exc_cnt = len(campaign_set_df)  # 기본 제외 후 고객수
        if isinstance(limit_count, int):
            budget_exc = cust_after_exc_cnt - limit_count if cust_after_exc_cnt > limit_count else 0
            exclusion_budget_limit_df = pd.DataFrame(
                {"div": ["예산 제한"], "id": [""], "name": [""], "count": [budget_exc]}
            )
            summary_df = pd.concat([summary_df, exclusion_budget_limit_df])
            cust_after_exc_cnt = (
                limit_count if cust_after_exc_cnt > limit_count else cust_after_exc_cnt
            )

        total_exc_cnt = tot_custs - cust_after_exc_cnt
        total_exc_df = pd.DataFrame(
            {
                "div": ["제외 고객 합산(중복 제외)"],
                "id": [""],
                "name": [""],
                "count": [total_exc_cnt],
            }
        )
        summary_df = pd.concat([summary_df, total_exc_df]).reset_index(drop=True)
        summary_dict = summary_df.to_dict("records")  # pyright: ignore [reportArgumentType]

        message = f"전체 타겟고객(제외조건 미반영) {tot_custs:,}명 중, 제외조건 적용 후 {total_exc_cnt:,}명의 고객이 제외되었습니다. \n{tot_custs - total_exc_cnt:,}명의 고객이 캠페인 대상으로 선정되었습니다."

        return ExcludeCustomerDetail(
            excl_message=message,
            excl_detail_stats=[
                ExcludeCustomerDetailStats(
                    div=summary["div"],
                    id=summary["id"],
                    name=summary["name"],
                    count=summary["count"],
                )
                for summary in summary_dict
            ],
        )
