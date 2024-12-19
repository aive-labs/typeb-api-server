import numpy as np
import pandas as pd
from sqlalchemy.orm import Session

from src.campaign.infra.sqlalchemy_query.campaign_set.apply_personalized_option import (
    apply_personalized_option,
)
from src.campaign.infra.sqlalchemy_query.campaign_set.recipient_custom_contents_mapping import (
    recipient_custom_contents_mapping,
)
from src.campaign.infra.sqlalchemy_query.delete_campaign_sets import (
    delete_campaign_sets,
)
from src.campaign.infra.sqlalchemy_query.get_audience_rank_between import (
    get_audience_rank_between,
)
from src.campaign.infra.sqlalchemy_query.get_customers_for_expert_campaign import (
    get_customers_for_expert_campaign,
)
from src.campaign.infra.sqlalchemy_query.recreate_basic_campaign import (
    add_ltv_frequency,
    check_customer_data_consistency,
    exclude_customers_from_exclusion_audiences,
    exclude_customers_from_exclusion_campaign,
)
from src.campaign.routes.dto.request.campaign_set_update import CampaignSetUpdateDetail
from src.common.enums.campaign_media import CampaignMedia
from src.common.utils.data_converter import DataConverter
from src.common.utils.date_utils import localtime_converter
from src.main.exceptions.exceptions import ConsistencyException
from src.message_template.enums.message_type import MessageType


def recreate_expert_campaign_set(
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
    campaign_set_update: list[CampaignSetUpdateDetail],
    db: Session,
):
    delete_campaign_sets(campaign_id, db)

    initial_msg_type = {
        CampaignMedia.KAKAO_ALIM_TALK.value: MessageType.KAKAO_ALIM_TEXT.value,
        CampaignMedia.KAKAO_FRIEND_TALK.value: MessageType.KAKAO_IMAGE_GENERAL.value,
        CampaignMedia.TEXT_MESSAGE.value: MessageType.LMS.value,
    }

    campaign_msg_type = initial_msg_type[media]

    # 전략테마에 속하는 audience_id 조회
    # 전략테마 하나에 여러 audience_id가 있을 수도 있음
    strategy_themes_df = pd.DataFrame(
        [set_update.model_dump() for set_update in campaign_set_update]
    )
    strategy_themes_df["rep_nm_list"] = strategy_themes_df["rep_nm_list"].apply(
        lambda x: x[0] if x else np.nan
    )
    strategy_themes_df.rename(columns={"rep_nm_list": "rep_nm"}, inplace=True)

    print("update strategy_themes_df")
    print(strategy_themes_df)

    strategy_themes_df = strategy_themes_df.sort_values("set_sort_num")

    audience_ids = list(set(strategy_themes_df["audience_id"]))

    # strategy_themes_df = DataConverter.convert_query_to_df(
    #     get_strategy_theme_audience_mapping_query(selected_themes, db)
    # )
    recsys_model_ids = list(set(strategy_themes_df["recsys_model_id"]))

    # cust_campaign_object : 고객 audience_ids
    customer_query = get_customers_for_expert_campaign(audience_ids, recsys_model_ids, db)
    # columns: [cus_cd, audience_id, ltv_frequency, age_group_10]
    cust_audiences_df = DataConverter.convert_query_to_df(customer_query)
    print("cust_audiences_df")
    print(cust_audiences_df)

    # audience_id 특정 조건(반응률 등)에 따라 순위 생성
    audience_rank_between = get_audience_rank_between(audience_ids, db)
    audience_rank_between_df = DataConverter.convert_query_to_df(audience_rank_between)
    print("audience_rank_between_df")
    print(audience_rank_between_df)

    # strategy_themes_df의 audience_id에 audience 순위 매핑
    strategy_themes_df = pd.merge(
        strategy_themes_df, audience_rank_between_df, on="audience_id", how="inner"
    )

    campaign_set_df_merged = cust_audiences_df.merge(
        strategy_themes_df, on="audience_id", how="inner"
    )

    print("cust_audiences_df")
    print(cust_audiences_df)

    print("campaign_set_df_merged")
    print(campaign_set_df_merged)

    # cus_cd가 가장 낮은 숫자의 set_sort_num에 속하게 하기 위해
    print('campaign_set_df_merged.groupby(["cus_cd"])["set_sort_num"].idxmin()')
    print(campaign_set_df_merged.groupby(["cus_cd"])["set_sort_num"].idxmin())
    campaign_set_df = campaign_set_df_merged.loc[
        campaign_set_df_merged.groupby(["cus_cd"])["set_sort_num"].idxmin()
    ]

    del campaign_set_df_merged

    # 제외 캠페인 고객 필터
    if campaigns_exc:
        campaign_set_df = exclude_customers_from_exclusion_campaign(
            campaign_set_df, campaigns_exc, db
        )

    # 제외 타겟 오디언스 고객 필터
    if audiences_exc:
        campaign_set_df = exclude_customers_from_exclusion_audiences(
            audiences_exc, campaign_set_df, db
        )

    # 예산 적용
    limit_count = None
    if isinstance(limit_count, int):
        campaign_set_df = add_ltv_frequency(campaign_set_df, limit_count, db)

    # 고객 데이터 정합성 예외처리
    check_customer_data_consistency(campaign_set_df)

    # offer
    # 고객 별 오퍼 & 전략 정보 붙이기: 전략 상 저장된 오퍼정보가 아닌 추천 마스터 테이블 row는 일부 제외될 수 있음
    # 오퍼가 존재하면 붙힌다.
    # offer_query = get_first_offer_by_strategy_theme(selected_themes, db)
    # columns: [strategy_theme_id, coupon_no, coupon_name, benefit_type,
    #           benefit_type_name, {benefit_price} or {benefit_percentage}]
    # offer_df = DataConverter.convert_query_to_df(offer_query)

    # campaign_set_df = campaign_set_df.merge(offer_df, on="strategy_theme_id", how="left")
    print("campaign_set_df")
    print(campaign_set_df)

    # 세트 고객 집계
    group_keys = [
        "strategy_theme_id",
        "strategy_theme_name",
        "recsys_model_id",
        "audience_id",
        "audience_name",
        "coupon_no",
        "coupon_name",
    ]
    cols = group_keys + ["set_sort_num", "rep_nm"]

    campaign_set = campaign_set_df[cols]
    campaign_set = campaign_set.drop_duplicates()

    print("-----------------------------------------------------------------------")

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

    # 발송대상
    # 개인화 타겟팅 옵션 적용 - group_category, group_val 세팅
    campaign_set_df = apply_personalized_option(campaign_set_df, is_personalized)

    # 발송대상 2) 커스텀에서는 전략에서 선택한 콘텐츠를 매핑함
    # 있으면 매핑 없으면 None
    campaign_set_df = recipient_custom_contents_mapping(campaign_set_df, selected_themes, db)

    campaign_set_df["campaign_id"] = campaign_id
    campaign_set_df["send_result"] = None
    campaign_set_df["created_at"] = created_at
    campaign_set_df["created_by"] = user_id
    campaign_set_df["updated_at"] = created_at
    campaign_set_df["updated_by"] = user_id

    # ***캠페인 세트  campaign_set_merged 완성***
    campaign_set_merged = campaign_set_merged.replace({np.nan: None})

    group_keys = ["set_sort_num", "group_sort_num"]
    df_grouped1 = (  # pyright: ignore [reportCallIssue]
        campaign_set_df.groupby(group_keys)[["cus_cd"]]
        .agg({"cus_cd": "nunique"})
        .rename(columns={"cus_cd": "recipient_group_count"})
    )

    if set_cus_count["recipient_count"].sum() != df_grouped1["recipient_group_count"].sum():
        raise ConsistencyException(
            detail={"code": "campaign/set/create", "message": "고객 수가 일치하지 않습니다."},
        )

    select_cols = ["set_group_category", "set_group_val", "contents_id", "contents_name"]
    df_grouped2 = campaign_set_df.groupby(group_keys)[select_cols].agg(
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
                "msg_type": campaign_msg_type,
                "recipient_count": row["recipient_count"],
                "group_send_count": None,
                "created_at": row["created_at"],
                "created_by": row["created_by"],
                "updated_at": row["updated_at"],
                "updated_by": row["updated_by"],
            }
            group_dict_list.append(elem_dict)
        campaign_set_merged.at[idx, "set_group_list"] = group_dict_list

    return campaign_set_merged, campaign_set_df
