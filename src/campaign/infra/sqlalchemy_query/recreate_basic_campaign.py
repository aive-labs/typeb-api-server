import numpy as np
import pandas as pd

from src.campaign.infra.sqlalchemy_query.delete_campaign_sets import (
    delete_campaign_sets,
)
from src.campaign.infra.sqlalchemy_query.get_campaign_remind import get_campaign_remind
from src.campaign.infra.sqlalchemy_query.get_coupons_by_ids import get_coupons_by_ids
from src.campaign.infra.sqlalchemy_query.get_customer_by_audience_id import (
    get_customers_by_audience_id,
)
from src.campaign.infra.sqlalchemy_query.get_exclude_customer_list import (
    get_excluded_customer_list,
)
from src.campaign.infra.sqlalchemy_query.get_ltv import get_ltv
from src.common.enums.campaign_media import CampaignMedia
from src.common.utils.data_converter import DataConverter
from src.common.utils.date_utils import localtime_converter
from src.core.exceptions.exceptions import PolicyException
from src.message_template.enums.message_type import MessageType


def recreate_basic_campaign_set(
    db,
    shop_send_yn,
    user_id,
    campaign_id,
    campaign_group_id,
    media,
    msg_delivery_vendor,
    is_personalized,
    selected_themes,
    budget,
    campaigns_exc,
    audiences_exc,
    campaign_set_updated,
):
    # 캠페인 세트 삭제
    delete_campaign_sets(db, campaign_id)

    initial_msg_type = {
        CampaignMedia.KAKAO_ALIM_TALK.value: MessageType.KAKAO_ALIM_TEXT.value,
        CampaignMedia.TEXT_MESSAGE.value: MessageType.LMS.value,
    }
    budget_list = [(media, initial_msg_type[media])]
    remind_data = get_campaign_remind(db, campaign_id)
    for remind in remind_data:
        budget_list.append((remind.remind_media, initial_msg_type[remind.remind_media]))

    # 예산 적용 후
    # 수정필요 > 리마인드 있는 경우 리마인드에 따라서 예산 분배 변경
    # 리마인드 > 타입 동일
    limit_count = None

    # 예산 적용 후
    # 기본 캠페인에서는 입력된 set_seq 정보를 그대로 활용
    themes_df = pd.DataFrame(campaign_set_updated)
    themes_df = themes_df.sort_values("set_sort_num")

    audience_ids = list(set(themes_df["audience_id"]))
    offer_ids = list(set(themes_df["offer_id"]))

    # cust_campaign_object : 고객 audience_ids
    cust_audiences = get_customers_by_audience_id(audience_ids, db)
    #### Basic 캠페인에서는 SetSortNum이 항상 존재함.
    cust_audiences_df = DataConverter.convert_query_to_df(cust_audiences)
    campaign_set_df_merged = cust_audiences_df.merge(themes_df, on="audience_id", how="inner")
    ####방어로직###
    campaign_set_df = campaign_set_df_merged.loc[
        campaign_set_df_merged.groupby(["cus_cd"])["set_sort_num"].idxmin()
    ]
    del campaign_set_df_merged
    ##############

    # 제외 캠페인 고객 필터
    if campaigns_exc:
        exc_cus_query = get_excluded_customer_list(db, campaigns_exc)
        exc_cus_df = DataConverter.convert_query_to_df(exc_cus_query).rename(
            columns={"exc_cus_cd": "cus_cd"}
        )
        campaign_set_df = pd.merge(
            campaign_set_df, exc_cus_df, on="cus_cd", how="left", indicator=True
        )
        campaign_set_df = campaign_set_df[campaign_set_df["_merge"] == "left_only"].drop(
            columns=["_merge"]
        )

    # 제외 고객
    if audiences_exc:
        exc_aud_query = get_customers_by_audience_id(audiences_exc, db)
        exc_aud_df = DataConverter.convert_query_to_df(exc_aud_query)
        exc_aud_df = exc_aud_df.drop(columns=["audience_id", "purpose"])
        exc_aud_df = exc_aud_df.drop_duplicates("cus_cd")
        campaign_set_df = pd.merge(
            campaign_set_df, exc_aud_df, on="cus_cd", how="left", indicator=True
        )
        campaign_set_df = campaign_set_df[campaign_set_df["_merge"] == "left_only"].drop(
            columns=["_merge"]
        )

    ## 예산 적용
    if isinstance(limit_count, int):
        ltv_score = DataConverter.convert_queries_to_df(get_ltv(db))
        campaign_set_df = pd.merge(campaign_set_df, ltv_score, on="cus_cd", how="left")
        campaign_set_df["ltv_frequency"] = campaign_set_df["ltv_frequency"].fillna(0)
        campaign_set_df = campaign_set_df.sort_values(by="ltv_frequency", ascending=False)
        campaign_set_df = campaign_set_df.head(limit_count)

    if len(campaign_set_df) == 0:
        raise PolicyException(
            detail={"code": "campaign/set/create", "message": "대상 고객이 존재하지 않습니다."},
        )

    # 한개의 cus_cd가 두개이상의 set_sort_num을 가지는 경우를 확인하고 에러 표시
    if len(campaign_set_df["cus_cd"].unique()) != len(campaign_set_df):
        raise PolicyException(
            detail={"code": "campaign/set/create", "message": "중복된 고객이 존재합니다."},
        )

    offer_query = get_coupons_by_ids(db, offer_ids)
    offer_df = DataConverter.convert_query_to_df(offer_query)
    offer_df = offer_df.drop(columns=["offer_name"])
    # 고객 별 오퍼 & 전략 정보 붙이기: 전략 상 저장된 오퍼정보가 아닌 추천 마스터 테이블 row는 일부 제외될 수 있음
    # 오퍼가 존재하면 붙힌다.
    campaign_set_df = campaign_set_df.merge(offer_df, on="offer_id", how="left")

    ## 세트 고객 집계
    group_keys = [
        "campaign_theme_id",
        "campaign_theme_name",
        "recsys_model_id",
        "audience_id",
        "audience_name",
        "offer_id",
        "offer_name",
        "event_no",
    ]
    cols = group_keys + ["set_sort_num"]
    campaign_set = campaign_set_df[cols].drop_duplicates()
    set_cus_count = (
        campaign_set_df.groupby("set_sort_num")["cus_cd"]
        .nunique()
        .reset_index()
        .rename(columns={"cus_cd": "recipient_count"})
    )

    campaign_set_merged = campaign_set.merge(set_cus_count, on="set_sort_num", how="left")
    campaign_set_merged = campaign_set_merged.sort_values("set_sort_num").reset_index(drop=True)
    created_at = localtime_converter()

    campaign_set_merged["campaign_id"] = campaign_id
    campaign_set_merged["campaign_group_id"] = campaign_group_id
    campaign_set_merged["medias"] = media
    campaign_set_merged["is_confirmed"] = False
    campaign_set_merged["is_message_confirmed"] = False
    campaign_set_merged["is_group_added"] = False
    campaign_set_merged["is_personalized"] = is_personalized
    campaign_set_merged["created_at"] = created_at
    campaign_set_merged["created_by"] = user_id
    campaign_set_merged["updated_at"] = created_at
    campaign_set_merged["updated_by"] = user_id

    # set recipient
    set_cus_items_df = campaign_set_df[["cus_cd", "recsys_model_id", "set_sort_num"]]

    set_cus_items_df["set_group_val"] = None
    set_cus_items_df["set_group_category"] = None
    set_cus_items_df["rep_nm"] = None
    set_cus_items_df["group_sort_num"] = 1
    set_cus_items_df["contents_id"] = None
    set_cus_items_df["contents_name"] = None
    set_cus_items_df["campaign_id"] = campaign_id
    set_cus_items_df["send_result"] = None
    set_cus_items_df["created_at"] = created_at
    set_cus_items_df["created_by"] = user_id
    set_cus_items_df["updated_at"] = created_at
    set_cus_items_df["updated_by"] = user_id

    # ***캠페인 세트  campaign_set_merged 완성***
    campaign_set_merged["rep_nm_list"] = None
    campaign_set_merged = campaign_set_merged.replace({np.nan: None})

    group_keys = ["set_sort_num", "group_sort_num"]
    df_grouped1 = (  # pyright: ignore [reportCallIssue]
        set_cus_items_df.groupby(group_keys)[["cus_cd"]]
        .agg({"cus_cd": "nunique"})
        .rename(columns={"cus_cd": "recipient_group_count"})
    )

    select_cols = ["set_group_category", "set_group_val", "contents_id", "contents_name"]
    df_grouped2 = set_cus_items_df.groupby(group_keys)[select_cols].agg(
        {
            "set_group_category": "first",
            "set_group_val": "first",
            "contents_id": "first",
            "contents_name": "first",
        }
    )

    res_groups_df = pd.concat(  # pyright: ignore [reportCallIssue]
        [df_grouped1, df_grouped2], axis=1  # pyright: ignore [reportArgumentType]
    ).reset_index()  # pyright: ignore [reportCallIssue]
    res_groups_df = res_groups_df.replace({np.nan: None})

    campaign_set_merged["set_group_list"] = None
    msg_type = initial_msg_type[media]

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
                "media": row["medias"],
                "msg_type": msg_type,
                "recipient_count": row["recipient_count"],
                "group_send_count": None,
                "created_at": row["created_at"],
                "created_by": row["created_by"],
                "updated_at": row["updated_at"],
                "updated_by": row["updated_by"],
            }
            group_dict_list.append(elem_dict)
        campaign_set_merged.at[idx, "set_group_list"] = group_dict_list

    return campaign_set_merged, set_cus_items_df
