import numpy as np
import pandas as pd
from fastapi.encoders import jsonable_encoder
from sqlalchemy import delete

from src.campaign.infra.entity.campaign_set_groups_entity import CampaignSetGroupsEntity
from src.campaign.infra.entity.campaign_set_recipients_entity import (
    CampaignSetRecipientsEntity,
)
from src.campaign.infra.entity.campaign_sets_entity import CampaignSetsEntity
from src.campaign.infra.sqlalchemy_query.campaign_set.recipient_custom_contents_mapping import (
    recipient_custom_contents_mapping,
)
from src.campaign.infra.sqlalchemy_query.create_set_group_messages import (
    create_set_group_messages,
)
from src.campaign.infra.sqlalchemy_query.get_campaign_remind import get_campaign_remind
from src.campaign.infra.sqlalchemy_query.get_contents_name import (
    get_rep_nm_by_contents_id,
)
from src.campaign.infra.sqlalchemy_query.get_customer_by_audience_id import (
    get_customers_by_audience_id,
)
from src.campaign.infra.sqlalchemy_query.get_customers_for_expert_campaign import (
    get_customers_for_expert_campaign,
)
from src.campaign.infra.sqlalchemy_query.get_exclude_customer_list import (
    get_excluded_customer_list,
)
from src.campaign.infra.sqlalchemy_query.get_ltv import get_ltv
from src.campaign.utils.utils import (
    split_dataframe_by_ratios,
    split_df_stratified_by_column,
)
from src.common.model.campaign_media import CampaignMedia
from src.common.utils.data_converter import DataConverter
from src.common.utils.date_utils import localtime_converter
from src.main.exceptions.exceptions import PolicyException
from src.message_template.model.message_type import MessageType


class CampaignManager:
    """캠페인 관리 클래스"""

    def __init__(self, db, shop_send_yn, user_id, recurring_campaign_id=None, cls_status=None):
        self.db = db
        self.shop_send_yn = shop_send_yn
        self.user_id = user_id
        self.cls_status = cls_status
        self.recurring_campaign_id = recurring_campaign_id
        self.campaign_obj = None
        self.campaign_id = None
        self.initial_msg_type = {
            CampaignMedia.KAKAO_ALIM_TALK.value: MessageType.KAKAO_ALIM_TEXT.value,
            CampaignMedia.KAKAO_FRIEND_TALK.value: MessageType.KAKAO_IMAGE_GENERAL.value,
            CampaignMedia.TEXT_MESSAGE.value: MessageType.LMS.value,
        }

    def _load_campaign_object(self, campaign_obj_dict):
        """캠페인 수정관련 기본 데이터 호출 함수
        1. 캠페인 set 데이터 호출
        2. 캠페인 group 데이터 호출
        """
        self.campaign_id = campaign_obj_dict.get("campaign_id")
        self.campaign_obj_dict = campaign_obj_dict

        if self.recurring_campaign_id:
            self.filter_campaign_id = self.recurring_campaign_id
        else:
            self.filter_campaign_id = self.campaign_id

        self.campaign_set_update = (
            self.db.query(CampaignSetsEntity)
            .filter(CampaignSetsEntity.campaign_id == self.filter_campaign_id)
            .order_by(CampaignSetsEntity.set_sort_num.asc())
        )
        self.campaign_set_df = DataConverter.convert_query_to_df(self.campaign_set_update)

        self.campaign_group_update = (
            self.db.query(CampaignSetGroupsEntity)
            .filter(CampaignSetGroupsEntity.campaign_id == self.filter_campaign_id)
            .order_by(
                CampaignSetGroupsEntity.set_sort_num.asc(),
                CampaignSetGroupsEntity.group_sort_num.asc(),
            )
        )
        self.campaign_group_df = DataConverter.convert_query_to_df(self.campaign_group_update)

        if campaign_obj_dict.get("campaign_type_code") == "basic":
            self.model = "basic"
        else:
            self.model = "custom"

    def _custom_preprocessing(self, cust_audiences_df):
        """커스텀 캠페인 데이터 전처리 함수
        1. 커스텀 캠페인 데이터 호출
        2. 커스텀 캠페인 데이터 전처리
          - contents_id, rep_nm, coverage_score, rep_nm2, coverage_score2
          - 번들 추천으로 인해 rep_nm2, coverage_score2 추가
        """
        # 커스텀 캠페인 모델용도
        cust_audiences_df = cust_audiences_df.drop(columns=["recsys_model_id", "coupon_no"])
        cust_rec_df = self.campaign_set_df.merge(cust_audiences_df, on="audience_id", how="right")

        cust_rec_df = cust_rec_df.sort_values(by="set_sort_num", ascending=True).drop_duplicates(
            "cus_cd", keep="first"
        )

        if self.campaign_obj_dict.get("is_personalized"):
            cust_rec_df.loc[:, "age_group_10"] = cust_rec_df.loc[:, "age_group_10"].fillna("")
            cust_rec_df = cust_rec_df.rename(columns={"age_group_10": "set_group_val"})
            cust_rec_df["set_group_category"] = "age_group_10"
        else:
            cust_rec_df["set_group_val"] = None
            cust_rec_df["set_group_category"] = None

        selected_themes = self.campaign_obj_dict.get("strategy_theme_ids")

        cust_rec_df = recipient_custom_contents_mapping(self.db, cust_rec_df, selected_themes)
        cust_rec_df["rep_nm"] = None

        # assign set_sort_num
        set_sort_num_df = cust_rec_df[["cus_cd", "audience_id", "coupon_no"]]
        set_sort_num_df = set_sort_num_df.drop_duplicates()

        # join_key -> campaign_theme_id?
        set_sort_num_df = self.campaign_set_df[
            ["set_seq", "set_sort_num", "recsys_model_id", "audience_id", "coupon_no"]
        ].merge(set_sort_num_df, on=["audience_id", "coupon_no"], how="left")

        return cust_rec_df, set_sort_num_df

    def create_recurred_set_group(self, cust_audiences_df, recipient_df, campaign_obj_dict):

        recipient_df_join = recipient_df[["cus_cd", "group_sort_num", "media", "msg_type"]].copy()
        cust_audiences_df = cust_audiences_df.merge(recipient_df_join, on="cus_cd", how="left")
        if excluded_cnt := len(cust_audiences_df[cust_audiences_df["group_sort_num"].isnull()]) > 0:
            print(f"누락된 고객이 {excluded_cnt}명 입니다.")

        cols = [
            "campaign_group_id",
            "medias",
            "set_sort_num",
            "strategy_theme_id",
            "strategy_theme_name",
            "recsys_model_id",
            "audience_id",
            "audience_name",
            "coupon_no",
            "coupon_name",
            "is_message_confirmed",
        ]
        campaign_set = cust_audiences_df[cols].drop_duplicates()
        set_cus_count = (
            cust_audiences_df.groupby("set_sort_num")["cus_cd"]
            .nunique()
            .reset_index()
            .rename(columns={"cus_cd": "recipient_count"})
        )

        created_at = localtime_converter()
        campaign_set_merged = campaign_set.merge(set_cus_count, on="set_sort_num", how="left")
        campaign_set_merged = campaign_set_merged.sort_values("set_sort_num").reset_index(drop=True)
        campaign_set_merged["is_group_added"] = False
        campaign_set_merged["media_cost"] = None
        campaign_set_merged["campaign_id"] = campaign_obj_dict.get("campaign_id")
        campaign_set_merged["is_personalized"] = campaign_obj_dict.get("is_personalized")
        campaign_set_merged["created_at"] = created_at
        campaign_set_merged["created_by"] = self.user_id
        campaign_set_merged["updated_at"] = created_at
        campaign_set_merged["updated_by"] = self.user_id
        campaign_set_merged["rep_nm_list"] = None
        campaign_set_merged["set_group_list"] = None
        campaign_set_merged = campaign_set_merged.replace({np.nan: None})

        if campaign_obj_dict.get("is_personalized") is False:
            group_keys = ["set_sort_num", "group_sort_num", "media", "msg_type"]
            res_groups_df = (
                cust_audiences_df.groupby(group_keys)[["cus_cd"]]
                .agg({"cus_cd": "nunique"})
                .rename(columns={"cus_cd": "recipient_group_count"})
            )
            res_groups_df = res_groups_df.reset_index()
            res_groups_df = res_groups_df.replace({np.nan: None})
            res_groups_df["set_group_category"] = None
            res_groups_df["set_group_val"] = None
            res_groups_df["contents_id"] = None
            res_groups_df["contents_name"] = None

        elif campaign_obj_dict.get("is_personalized") is True:
            group_keys = [
                "set_sort_num",
                "group_sort_num",
                "media",
                "msg_type",
                "set_group_category",
                "set_group_val",
                "contents_id",
                "contents_name",
            ]
            res_groups_df = (
                cust_audiences_df.groupby(group_keys)[["cus_cd"]]
                .agg({"cus_cd": "nunique"})
                .rename(columns={"cus_cd": "recipient_group_count"})
            )
            res_groups_df = res_groups_df.reset_index()
            res_groups_df = res_groups_df.replace({np.nan: None})
        else:
            res_groups_df = None

        return campaign_set_merged, res_groups_df

    def save_recurred_set_group(self, campaign_set_merged, res_groups_df):

        for idx, row in campaign_set_merged.iterrows():
            set_sort_num = row["set_sort_num"]
            group_dict_list = []
            for _, row_g in res_groups_df[res_groups_df["set_sort_num"] == set_sort_num].iterrows():
                elem_dict = {
                    "group_sort_num": row_g["group_sort_num"],
                    "set_group_category": row_g["set_group_category"],
                    "set_group_val": row_g["set_group_val"],
                    "recipient_group_rate": round(
                        row_g["recipient_group_count"] / row["recipient_count"], 3
                    ),
                    "recipient_group_count": row_g["recipient_group_count"],
                    "contents_id": row_g["contents_id"],
                    "contents_name": row_g["contents_name"],
                    "campaign_id": row["campaign_id"],
                    "set_sort_num": row["set_sort_num"],
                    "media": row_g["media"],
                    "msg_type": row_g["msg_type"],
                    "recipient_count": row["recipient_count"],
                    "group_send_count": None,
                    "created_at": row["created_at"],
                    "created_by": row["created_by"],
                    "updated_at": row["updated_at"],
                    "updated_by": row["updated_by"],
                }
                group_dict_list.append(elem_dict)

            campaign_set_merged.at[idx, "set_group_list"] = group_dict_list

        # campaign_set, set_group Insert
        db = self.db
        campaign_df = campaign_set_merged
        campaign_set_columns = [column.name for column in CampaignSetsEntity.__table__.columns]
        columns_col_list = campaign_df.columns.tolist()
        set_col_to_insert = [
            set_col for set_col in campaign_set_columns if set_col in columns_col_list
        ]
        set_col_to_insert.append("set_group_list")

        # CampaignSets 인서트할 컬럼 필터
        campaign_set_df = campaign_df[set_col_to_insert]

        for _, row in campaign_set_df.iterrows():
            # CampaignSets 인서트
            set_list = row[set_col_to_insert].to_dict()
            set_list_insert = {
                key: value for key, value in set_list.items() if key != "set_group_list"
            }
            set_req = CampaignSetsEntity(**set_list_insert)

            set_group_req_list = []
            for set_group in row["set_group_list"]:
                # CampaignSetGroups 인서트
                set_group_req = CampaignSetGroupsEntity(**set_group)

                if set_group_req.contents_id:
                    rep_nm = get_rep_nm_by_contents_id(set_group_req.contents_id, db)
                    set_group_req.rep_nm = rep_nm

                set_group_req_list.append(set_group_req)

            set_req.set_group_list = set_group_req_list
            db.add(set_req)

        db.commit()

        return True

    def prepare_campaign_recipients(self, campaign_obj_dict, add_new_group=True):
        """캠페인 수신자 데이터 호출 함수"""
        self._load_campaign_object(campaign_obj_dict)
        if len(self.campaign_set_df) == 0:
            # 캠페인 세트가 없는 경우 예외처리 # ex 기본 캠페인
            return None

        if add_new_group:
            if campaign_obj_dict.get("is_personalized") == False:
                print("warning: 개인화 설정에서만 add_new_group옵션을 True로 사용할 수 있습니다.")
                print("warning: add_new_group옵션이 False로 설정됩니다.")
                add_new_group = False

        media_list = campaign_obj_dict.get("medias").split(",")
        media = (
            "tms" if "tms" in media_list else media_list[0]
        )  # tms가 포함되어 있으면 tms로 설정, tms가 없으면 알림톡 or 친구톡으로 설정
        budget_list = [(media, self.initial_msg_type.get(media))]
        remind_data = get_campaign_remind(self.db, campaign_obj_dict.get("campaign_id"))
        for remind in remind_data:
            budget_list.append((remind.remind_media, self.initial_msg_type[remind.remind_media]))

        limit_count = None

        # audience 추출
        audience_ids = self.campaign_set_df["audience_id"].unique().tolist()
        print("audience_ids")
        print(audience_ids)

        # 고객 목록 호출
        recommend_models = self.campaign_set_df["recsys_model_id"].unique().tolist()
        print("recommend_models")
        print(recommend_models)
        cust_audiences = get_customers_for_expert_campaign(audience_ids, recommend_models, self.db)
        cust_audiences_df = DataConverter.convert_query_to_df(cust_audiences)

        ## 제외고객 필터링 적용
        campaigns_exc = campaign_obj_dict.get("campaigns_exc")
        audiences_exc = campaign_obj_dict.get("audiences_exc")
        if campaigns_exc:
            exc_cus_query = get_excluded_customer_list(self.db, campaigns_exc)
            exc_cus_df = DataConverter.convert_query_to_df(exc_cus_query).rename(
                columns={"exc_cus_cd": "cus_cd"}
            )
            exc_cus_df = exc_cus_df.drop_duplicates("cus_cd")
            cust_audiences_df = pd.merge(
                cust_audiences_df, exc_cus_df, on="cus_cd", how="left", indicator=True
            )
            cust_audiences_df = cust_audiences_df[cust_audiences_df["_merge"] == "left_only"].drop(
                columns=["_merge"]
            )

        if audiences_exc:
            exc_aud_query = get_customers_by_audience_id(audiences_exc, self.db)
            exc_aud_df = DataConverter.convert_query_to_df(exc_aud_query)
            exc_aud_df = exc_aud_df.drop(columns=["audience_id"])
            exc_aud_df = exc_aud_df.drop_duplicates("cus_cd")
            cust_audiences_df = pd.merge(
                cust_audiences_df, exc_aud_df, on="cus_cd", how="left", indicator=True
            )
            cust_audiences_df = cust_audiences_df[cust_audiences_df["_merge"] == "left_only"].drop(
                columns=["_merge"]
            )

        ## 예산 적용, 커스텀에서는 고객을 가져올때 ltv가 없으므로 포함
        if isinstance(limit_count, int):
            ltv_score = DataConverter.convert_queries_to_df(get_ltv(self.db))
            cust_audiences_df = pd.merge(cust_audiences_df, ltv_score, on="cus_cd", how="left")
            cust_audiences_df["ltv_frequency"] = cust_audiences_df["ltv_frequency"].fillna(0)
            cust_audiences_df = cust_audiences_df.sort_values(by="ltv_frequency", ascending=False)
            cust_audiences_df = cust_audiences_df.head(limit_count)

        if len(cust_audiences_df) == 0:
            raise PolicyException(
                detail={
                    "code": "campaign/set/create",
                    "message": "대상 고객이 존재하지 않습니다.",
                },
            )

        ## 기본 캠페인 및 그룹별 분배 (케이스 1)
        if (
            campaign_obj_dict.get("campaign_type_code") == "basic"
            or campaign_obj_dict.get("is_personalized") == False
        ):
            campaign_set_df = self.campaign_set_df.merge(
                cust_audiences_df, on="audience_id", how="right"
            )
            campaign_set_df["age_group_10"] = campaign_set_df["age_group_10"].fillna("")
            cust_audiences_df = campaign_set_df.sort_values(
                by="set_sort_num", ascending=True
            ).drop_duplicates("cus_cd", keep="first")
            cust_audiences_agg = (
                cust_audiences_df.groupby("set_sort_num")["cus_cd"].nunique().reset_index()
            )

            unique_set_sort_num = self.campaign_group_df["set_sort_num"].unique().tolist()
            # 1. 비율 > 그룹이 늘어날 수 없음 / 그대로 유지
            # campaign_type_code = basic 인 경우 그룹은 비율으로만 분배
            # campaign_type_code = custom 이면서 is_personalized = False 인 경우 그룹은 비율으로만 분배
            # 그룹별 비율 계산
            recipient_df = pd.DataFrame()
            for set_sort_num in unique_set_sort_num:
                set_df = cust_audiences_df[["cus_cd", "set_sort_num", "age_group_10"]][
                    cust_audiences_df["set_sort_num"] == set_sort_num
                ]
                sub_group = self.campaign_group_df[
                    self.campaign_group_df["set_sort_num"] == set_sort_num
                ]
                ratio_tuple = list(
                    zip(sub_group["group_sort_num"], sub_group["recipient_group_rate"])
                )
                if len(set_df) <= 1000:
                    result_df = split_dataframe_by_ratios(set_df, ratio_tuple)
                else:
                    result_df = split_df_stratified_by_column(set_df, ratio_tuple, "age_group_10")
                result_df["group_sort_num"] = result_df["group_sort_num"].apply(int)

                group_info = sub_group[
                    ["set_sort_num", "group_sort_num", "media", "msg_type"]
                ].copy()
                result_df = result_df.merge(
                    group_info, on=["set_sort_num", "group_sort_num"], how="left"
                )

                recipient_df = pd.concat([recipient_df, result_df])

            group_summary = (
                recipient_df.groupby(["set_sort_num", "group_sort_num"])
                .size()
                .reset_index(name="recipient_count")
            )
            group_summary["recipient_count"] = group_summary["recipient_count"].apply(int)
            group_summary["set_sort_num"] = group_summary["set_sort_num"].apply(int)
            group_set_summary = (
                group_summary.groupby("set_sort_num")["recipient_count"]
                .sum()
                .reset_index(name="total_recipient_count")
            )

            if self.recurring_campaign_id:
                # 주기성 - is_personalized = False

                print("cust_audiences_df.columns")
                print(cust_audiences_df.columns)

                campaign_set_merged, res_groups_df = self.create_recurred_set_group(
                    cust_audiences_df, recipient_df, campaign_obj_dict
                )
                self.save_recurred_set_group(campaign_set_merged, res_groups_df)

            else:
                # 일회성 - 기본캠페인
                # 세트 데이터 업데이트
                set_obj = self.campaign_set_update.all()
                for _, set in enumerate(set_obj):
                    set.recipient_count = int(
                        cust_audiences_agg.loc[
                            cust_audiences_agg["set_sort_num"] == set.set_sort_num, "cus_cd"
                        ].values[0]
                    )

                # 그룹 데이터 업데이트
                set_group_obj = self.campaign_group_update.all()
                for _, group in enumerate(set_group_obj):
                    group.recipient_group_count = int(
                        group_summary.loc[
                            (group_summary["set_sort_num"] == group.set_sort_num)
                            & (group_summary["group_sort_num"] == group.group_sort_num),
                            "recipient_count",
                        ].values[0]
                    )

                ## check total count
                for _, set in enumerate(set_obj):
                    if (
                        set.recipient_count
                        != group_set_summary.loc[
                            group_set_summary["set_sort_num"] == set.set_sort_num,
                            "total_recipient_count",
                        ].values[0]
                    ):
                        raise Exception("수신자 수가 일치하지 않습니다.")
                group_rec = self.campaign_group_df[
                    ["set_sort_num", "group_sort_num", "contents_id", "rep_nm"]
                ].drop_duplicates()
                recipient_df = recipient_df.merge(
                    group_rec, on=["set_sort_num", "group_sort_num"], how="left"
                )

        # 2. 개인화 > 그룹이 변경될 수 있음 / 줄거나 늘 수 있음
        # 개인화 캠페인 - 세그먼트, 커스텀, 신상품
        else:
            cust_rec_df, set_sort_num_df = self._custom_preprocessing(cust_audiences_df)

            if self.recurring_campaign_id and self.model == "custom":
                # 주기성 - 커스텀캠페인 is_personalized = True
                group_sort_num_df = cust_rec_df[
                    ["cus_cd", "set_group_category", "set_group_val", "age_group_10"]
                ]

                group_sort_num_subset = set_sort_num_df[["set_sort_num", "cus_cd"]]
                group_sort_num_subset = group_sort_num_subset.merge(
                    group_sort_num_df, on="cus_cd", how="inner"
                )

                org_group_df = self.campaign_group_df[
                    ["set_sort_num", "set_group_val", "group_sort_num", "media", "msg_type"]
                ]
                group_sort_num_subset = group_sort_num_subset.merge(
                    org_group_df, on=["set_sort_num", "set_group_val"], how="left"
                )

                # 'set_group_val'을 기준으로 정렬, None 값이 있는 경우는 마지막으로
                group_sort_num_subset = group_sort_num_subset.sort_values(
                    by=["set_sort_num", "group_sort_num"], na_position="last"
                )

                max_num = max(group_sort_num_subset["group_sort_num"]) + 1

                group_sort_num_subset["group_sort_num"] = group_sort_num_subset[
                    "group_sort_num"
                ].apply(lambda x: max_num if pd.isna(x) else x)
                group_sort_num_subset["group_sort_num"] = (
                    group_sort_num_subset["group_sort_num"].rank(method="dense").astype(int)
                )

                recipient_df = group_sort_num_subset
                campaign_set_merged, res_groups_df = self.create_recurred_set_group(
                    cust_rec_df, recipient_df, campaign_obj_dict
                )
                self.save_recurred_set_group(campaign_set_merged, res_groups_df)

            else:
                # 일회성 캠페인 -recipient
                set_sort_num_cnt = (
                    set_sort_num_df.groupby(["set_seq", "set_sort_num"])["cus_cd"]
                    .nunique()
                    .reset_index()
                )
                set_sort_num_cnt = set_sort_num_cnt.rename(columns={"cus_cd": "recipient_count"})

                if set_sort_num_cnt["recipient_count"].isna().sum() != 0:
                    raise PolicyException(
                        detail={
                            "code": "campaign/set/create",
                            "message": "set_sort_num이 사라진 데이터가 존재합니다.",
                        },
                    )

                # assign group_sort_num # set_sort_num_cnt 활용
                # 그룹 분배 동작
                group_sort_num_df = cust_rec_df[["cus_cd", "set_group_category", "set_group_val"]]

                group_sort_num_df = group_sort_num_df.drop_duplicates()
                group_sort_num_subset = set_sort_num_df[["set_seq", "set_sort_num", "cus_cd"]]
                group_sort_num_subset = group_sort_num_subset.merge(
                    group_sort_num_df, on="cus_cd", how="inner"
                )

                # print(group_sort_num_subset)
                group_sort_num_df = self.campaign_group_df[
                    [
                        "set_group_seq",
                        "group_sort_num",
                        "set_sort_num",
                        "set_seq",
                        "set_group_category",
                        "set_group_val",
                    ]
                ]

                if campaign_obj_dict.get("is_personalized"):
                    group_by_key = [
                        "set_seq",
                        "set_sort_num",
                        "set_group_category",
                        "set_group_val",
                    ]
                else:
                    group_by_key = ["set_seq", "set_sort_num"]

                group_sort_num_cnt_temp = (
                    group_sort_num_subset.groupby(group_by_key)["cus_cd"].nunique().reset_index()
                )
                group_sort_num_cnt_temp = group_sort_num_cnt_temp.rename(
                    columns={"cus_cd": "recipient_group_count"}
                )

                group_sort_num_df = group_sort_num_df.merge(
                    group_sort_num_cnt_temp, on=group_by_key, how="outer"
                )

                ## group recipient count 가 null 인 경우는 0으로 처리
                group_sort_num_df["recipient_group_count"] = group_sort_num_df[
                    "recipient_group_count"
                ].fillna(0)
                group_sort_num_df = group_sort_num_df.sort_values(
                    by=["set_sort_num", "group_sort_num"], ascending=[True, True]
                )
                group_sort_num_df = group_sort_num_df.reset_index(drop=True)
                group_sort_num_df["idx"] = group_sort_num_df.index + 1
                group_sort_num_df["rank"] = group_sort_num_df.groupby(
                    ["set_sort_num", "set_seq", "set_group_category"]
                )["idx"].rank(method="first", ascending=True)

                group_sort_num_df = group_sort_num_df.merge(
                    set_sort_num_cnt, on=["set_sort_num", "set_seq"], how="left"
                )
                group_sort_num_df = group_sort_num_df.replace({np.nan: None})

                recipient_df = group_sort_num_subset.merge(
                    group_sort_num_df, on=group_by_key, how="left"
                )
                recipient_df = recipient_df.drop(
                    columns=["idx", "recipient_count", "recipient_group_count"]
                )
                recipient_df = recipient_df.merge(
                    cust_rec_df[["cus_cd", "rep_nm", "contents_id"]], on="cus_cd", how="inner"
                )

                renewed = 0
                added = 0
                deleted = 0
                # add_new_group = False
                campaign_type_code = campaign_obj_dict.get("campaign_type_code")

                deleted_group_seq = []
                if add_new_group and campaign_obj_dict.get("is_personalized"):
                    # data update
                    # recipient_df = group_sort_num_subset.merge(group_sort_num_df, on=group_by_key, how='left')

                    set_obj = self.campaign_set_update.all()
                    for _, set in enumerate(set_obj):
                        set.recipient_count = int(
                            set_sort_num_cnt.loc[
                                set_sort_num_cnt["set_sort_num"] == set.set_sort_num,
                                "recipient_count",
                            ].values[0]
                        )

                    # remove unuse group seq
                    # group update
                    set_group_obj = self.campaign_group_update.all()
                    for _, group in enumerate(set_group_obj):
                        if group.set_group_seq not in group_sort_num_df["set_group_seq"].unique():
                            deleted += 1
                            deleted_group_seq.append(group.set_group_seq)
                    self.db.query(CampaignSetGroupsEntity).filter(
                        CampaignSetGroupsEntity.set_group_seq.in_(deleted_group_seq)
                    ).delete()
                    print(f"deleted: {deleted}")
                    group_sort_dict = group_sort_num_df.to_dict(orient="records")
                    new_set_groups = []
                    for _, group in enumerate(group_sort_dict):
                        if group["set_group_seq"] is not None:
                            set_group_obj_item = [
                                x
                                for x in set_group_obj
                                if x.set_group_seq == group["set_group_seq"]
                            ][0]
                            set_group_obj_item.recipient_group_count = int(
                                group["recipient_group_count"]
                            )
                            set_group_obj_item.group_sort_num = int(group["rank"])
                            set_group_obj_item.recipient_count = int(group["recipient_count"])
                            if set_group_obj_item.recipient_count != 0:
                                set_group_obj_item.recipient_group_rate = (
                                    set_group_obj_item.recipient_group_count
                                    / set_group_obj_item.recipient_count
                                )
                            else:
                                set_group_obj_item.recipient_group_rate = 0
                            renewed += 1
                        else:
                            related_set = [
                                x
                                for x in set_group_obj
                                if (
                                    x.set_sort_num == group["set_sort_num"]
                                    and x.group_sort_num == 1
                                )
                            ][0]
                            # SEG에서는 개인화 콘텐츠 / 커스텀에서는 그룹 내 콘텐츠
                            new_group = CampaignSetGroupsEntity(
                                set_sort_num=group["set_sort_num"],
                                contents_id=related_set.contents_id,
                                contents_name=related_set.contents_name,
                                set_seq=int(group["set_seq"]),
                                campaign_id=self.campaign_id,
                                media=related_set.media,
                                msg_type=related_set.msg_type,
                                group_sort_num=int(group["rank"]),
                                recipient_group_rate=group["recipient_group_count"]
                                / group["recipient_count"],
                                recipient_group_count=int(group["recipient_group_count"]),
                                recipient_count=int(group["recipient_count"]),
                                set_group_category=group["set_group_category"],
                                set_group_val=group["set_group_val"],
                                created_at=localtime_converter(),
                                created_by=self.user_id,
                                updated_at=localtime_converter(),
                                updated_by=self.user_id,
                            )
                            self.db.add(new_group)
                            self.db.flush()
                            new_set_groups.append(jsonable_encoder(new_group))
                            added += 1
                    if len(new_set_groups) > 0:
                        res = create_set_group_messages(
                            self.user_id,
                            self.campaign_id,
                            campaign_obj_dict["msg_delivery_vendor"],
                            campaign_obj_dict["start_date"],
                            campaign_obj_dict["send_date"],
                            campaign_obj_dict["has_remind"],
                            new_set_groups,
                            campaign_type_code,
                            self.db,
                        )
                        print(res)
                    print(f"renewed: {renewed}")
                    print(f"added: {added}")
                else:  # 그룹 추가 없이 업데이트만 진행
                    group_sort_num_df = group_sort_num_df[
                        group_sort_num_df["set_group_seq"].notna()
                    ]
                    group_sort_num_df["recipient_count"] = group_sort_num_df.groupby(
                        ["set_sort_num", "set_seq"]
                    )["recipient_group_count"].transform("sum")
                    print(group_sort_num_df)
                    set_obj = self.campaign_set_update.all()
                    set_data_temp = (
                        set_sort_num_cnt.groupby("set_sort_num")["recipient_count"]
                        .first()
                        .reset_index()
                    )
                    print(set_data_temp)
                    set_group_obj = self.campaign_group_update.all()
                    for _, set in enumerate(set_obj):
                        set.recipient_count = int(
                            set_data_temp.loc[
                                set_data_temp["set_sort_num"] == set.set_sort_num, "recipient_count"
                            ].values[0]
                        )

                    for _, group in enumerate(set_group_obj):
                        if group.set_group_seq not in group_sort_num_df["set_group_seq"].unique():
                            deleted += 1
                            deleted_group_seq.append(group.set_group_seq)
                    self.db.query(CampaignSetGroupsEntity).filter(
                        CampaignSetGroupsEntity.set_group_seq.in_(deleted_group_seq)
                    ).delete(synchronize_session="evaluate")
                    print(f"deleted: {deleted}")

                    group_sort_dict = group_sort_num_df.to_dict(orient="records")
                    for _, group in enumerate(group_sort_dict):
                        set_group_obj_item = [
                            x for x in set_group_obj if x.set_group_seq == group["set_group_seq"]
                        ][0]
                        set_group_obj_item.recipient_group_count = int(
                            group["recipient_group_count"]
                        )
                        set_group_obj_item.group_sort_num = int(group["rank"])
                        set_group_obj_item.recipient_count = int(group["recipient_count"])
                        if set_group_obj_item.recipient_count != 0:
                            set_group_obj_item.recipient_group_rate = (
                                set_group_obj_item.recipient_group_count
                                / set_group_obj_item.recipient_count
                            )
                        else:
                            set_group_obj_item.recipient_group_rate = 0
                        renewed += 1
                    print(f"renewed: {renewed}")
                    recipient_df = recipient_df[recipient_df["group_sort_num"].notna()]

        self.db.commit()
        print("recipient_df")
        print(recipient_df)
        return recipient_df

    def update_campaign_recipients(self, recipient_df):
        """캠페인 수신자 데이터 업데이트 함수"""
        # remove previous recipients
        delete_statement = delete(CampaignSetRecipientsEntity).where(
            CampaignSetRecipientsEntity.campaign_id == self.campaign_id
        )
        self.db.execute(delete_statement)

        recipient_df["campaign_id"] = self.campaign_id
        recipient_df = recipient_df.replace({np.nan: None})
        recipient_df["created_at"] = localtime_converter()
        recipient_df["created_by"] = self.user_id
        recipient_df["updated_at"] = localtime_converter()
        recipient_df["updated_by"] = self.user_id
        recipient_dict = recipient_df.to_dict(orient="records")
        self.db.bulk_insert_mappings(CampaignSetRecipientsEntity, recipient_dict)

        self.db.flush()
        return True
