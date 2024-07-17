import random

import numpy as np
import pandas as pd

from src.campaign.infra.entity.campaign_set_groups_entity import CampaignSetGroupsEntity
from src.campaign.infra.entity.campaign_set_recipients_entity import (
    CampaignSetRecipientsEntity,
)
from src.campaign.infra.entity.campaign_sets_entity import CampaignSetsEntity
from src.campaign.infra.sqlalchemy_query.delete_excluded_campaign_sets import (
    delete_excluded_campaign_sets,
)
from src.campaign.infra.sqlalchemy_query.get_campaign_remind import get_campaign_remind
from src.campaign.infra.sqlalchemy_query.get_coupons_by_ids import get_coupons_by_ids
from src.campaign.infra.sqlalchemy_query.get_customer_by_audience_id import (
    get_customers_by_audience_id,
)
from src.campaign.infra.sqlalchemy_query.get_exclude_customer_list import (
    get_excluded_customer_list,
)
from src.campaign.infra.sqlalchemy_query.get_rep_from_themes import get_rep_from_theme
from src.campaign.utils.campaign_creation import add_group_type
from src.common.enums.campaign_media import CampaignMedia
from src.common.utils.data_converter import DataConverter
from src.common.utils.date_utils import localtime_converter
from src.core.exceptions.exceptions import PolicyException
from src.message_template.enums.message_type import MessageType
from src.strategy.infra.entity.strategy_theme_offers_entity import (
    StrategyThemeOfferMappingEntity,
)


def recreate_new_collection_recommend_set(
    db,
    shop_send_yn,
    user_id,
    campaign_id,
    campaign_group_id,
    media,
    msg_delivery_vendor,
    is_personalized,
    strategy_theme_ids,
    budget,
    campaigns_exc,
    audiences_exc,
    campaign_set_updated,
):
    """신상품 추천 캠페인 세트 재생성"""
    ## 일부 삭제
    set_seqs = [i["set_seq"] for i in campaign_set_updated if i["set_seq"] is not None]
    delete_excluded_campaign_sets(db, campaign_id, set_seqs)

    # 캠페인 base
    initial_msg_type = {
        CampaignMedia.KAKAO_ALIM_TALK.value: MessageType.KAKAO_ALIM_TEXT.value,
        CampaignMedia.KAKAO_FRIEND_TALK.value: MessageType.KAKAO_IMAGE_GENERAL.value,
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
    campaign_msg_type = initial_msg_type[media]

    # 전략 테마 정보 가져오기
    themes_df = pd.DataFrame(campaign_set_updated)
    themes_df = themes_df.sort_values("set_sort_num").reset_index(drop=True)

    ## recipient 테이블에서 set_sort_num 변경하기#####################################
    set_obj = db.query(
        CampaignSetsEntity.set_seq,
        CampaignSetsEntity.set_sort_num.label("org_set_sort_num"),
    ).filter(CampaignSetsEntity.campaign_id == campaign_id)

    org_set_df = DataConverter.convert_query_to_df(set_obj)
    themes_df_compare = themes_df.merge(org_set_df, on="set_seq", how="inner")
    themes_df_compare = themes_df_compare[["set_seq", "set_sort_num", "org_set_sort_num"]]

    for _, row in themes_df_compare.iterrows():
        # CampaignSets
        db.query(CampaignSetsEntity).filter(
            CampaignSetsEntity.campaign_id == campaign_id,
            CampaignSetsEntity.set_seq == int(row["set_seq"]),
        ).update({"set_sort_num": int(row["set_sort_num"])})

        # CampaignSetGroups
        db.query(CampaignSetGroupsEntity).filter(
            CampaignSetGroupsEntity.campaign_id == campaign_id,
            CampaignSetGroupsEntity.set_seq == int(row["set_seq"]),
        ).update({"set_sort_num": int(row["set_sort_num"])})

        # CampaignSetRecipients
        db.query(CampaignSetRecipientsEntity).filter(
            CampaignSetRecipientsEntity.campaign_id == campaign_id,
            CampaignSetRecipientsEntity.set_sort_num == int(row["org_set_sort_num"]),
        ).update({"set_sort_num": int(row["set_sort_num"])})
    ###################################################################################

    ## 추가 테마에 대한 고객 : theme_id, audience_id, offer_type_code, offer_amount
    added_set_df = themes_df[themes_df["set_seq"].isnull()]

    # 새로 추가된 세트가 없는 경우
    if len(added_set_df) == 0:
        empty_df = []
        return empty_df, empty_df

    ### tobe check
    recsys_model_ids = list(set(added_set_df["recsys_model_id"].apply(int)))
    audience_ids = list(set(added_set_df["audience_id"]))
    # 전략 테마에서 사용되는 추천모델id를 seg_mstr 테이블에 검색하기 위한 model_id 변환작업 ex) 1 -> 1(top5) or 10(상품 개인회)
    # 전략 테마 레벨에서 상위로 매핑된 추천 모델이 존재함

    # 전략 대상 고객을 seg_mstr에서 필터링
    # ltv도 채워서 가져옴
    query = get_cus_with_seg(
        db,
        audience_ids,
        recsys_model_ids,
    )
    campaign_set_df = DataConverter.convert_query_to_df(query)
    if len(campaign_set_df) == 0:
        raise PolicyException(
            detail={"code": "campaign/set/create", "message": "적합한 고객이 존재하지 않습니다."},
        )

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
        exc_aud_query = get_customers_by_audience_id(db, audiences_exc)
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
        campaign_set_df["ltv_frequency"] = campaign_set_df["ltv_frequency"].fillna(0)
        campaign_set_df = campaign_set_df.sort_values(
            by="ltv_frequency", ascending=False
        )  # pyright: ignore [reportCallIssue]
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

    # Todo 삭제된 오디언스 X 테마 레벨의 고객 리스트업 및 추가
    selected_themes = themes_df.campaign_theme_id.unique().tolist()
    offer_id = (
        db.query(StrategyThemeOfferMappingEntity.coupon_no)
        .filter(StrategyThemeOfferMappingEntity.strategy_theme_id.in_(selected_themes))
        .first()
    )
    campaign_set_df.loc[:, "offer_id"] = offer_id[0]
    campaign_set_df.loc[:, "recsys_model_id"] = 8

    # 전략 테마에서 사용되는 오퍼 정보 가져오기
    offer_query = get_coupons_by_ids(db, offer_id)
    offer_df = DataConverter.convert_query_to_df(offer_query)

    campaign_set_df = campaign_set_df.merge(offer_df, on="offer_id", how="inner")

    # 추후 실험 설계를 위해서 각 오디언스의 대표 SEG와 audience_id를 매핑
    campaign_set_df = pd.merge(
        campaign_set_df, themes_df, on=["audience_id", "recsys_model_id"], how="inner"
    )

    if len(campaign_set_df) == 0:
        raise PolicyException(
            detail={"code": "campaign/set/create", "message": "적합한 오퍼가 존재하지 않습니다."},
        )

    # 세트 발송수 집계
    group_keys = [
        "strategy_theme_id",
        "strategy_theme_name",
        "recsys_model_id",
        "audience_id",
        "audience_name",
        "offer_id",
        "offer_name",
        "event_no",
    ]
    ## 세트 고객 집계 : set_sort_num 값이 모두 있어야 정상
    ## 개인화 모델
    cus_rec_qry = get_rep_from_theme(db, selected_themes)
    cus_rec_df = DataConverter.convert_query_to_df(cus_rec_qry)
    if len(cus_rec_df.rep_nm.unique()) != 1:
        raise PolicyException(
            detail={
                "code": "campaign/set/create",
                "message": "콘텐츠에 매핑된 대표상품은 1개여야 합니다.",
            },
        )

    contents_group = (
        campaign_set_df[["mix_lv1", "purpose_lv1"]].drop_duplicates().reset_index(drop=True)
    )
    # df = cus_rec_qry[['contents_id', 'contents_tags']]

    # get contents_id random choice by group
    match_data = []
    for _, purpose in zip(contents_group["mix_lv1"], contents_group["purpose_lv1"]):
        is_contains = []
        temp_df = cus_rec_df[cus_rec_df["contents_tags"].notnull()]
        id_list = cus_rec_df["contents_id"].tolist()
        for id, tags in zip(temp_df["contents_id"], temp_df["contents_tags"]):
            if purpose in tags:
                is_contains.append(id)
        if len(is_contains) > 0:
            random_id = random.choice(is_contains)
        else:
            random_id = random.choice(id_list)
        match_data.append(random_id)
    contents_group["contents_id"] = match_data

    ## merge
    prev_len = len(campaign_set_df)
    campaign_set_df = pd.merge(
        campaign_set_df, contents_group, on=["mix_lv1", "purpose_lv1"], how="inner"
    )
    if len(campaign_set_df) != prev_len:
        raise PolicyException(
            detail={
                "code": "campaign/set/create",
                "message": "고객 추천 상품 테이블이 일치하지 않습니다.",
            },
        )

    campaign_set_df = campaign_set_df.merge(
        cus_rec_df[["contents_id", "contents_name", "contents_url", "rep_nm"]],
        on=["contents_id"],
        how="inner",
    )
    if len(campaign_set_df) != prev_len:
        raise PolicyException(
            detail={
                "code": "campaign/set/create",
                "message": "고객 추천 상품 테이블이 일치하지 않습니다.",
            },
        )

    campaign_set_df["set_sort_num"] = campaign_set_df.groupby(group_keys).ngroup() + 1
    cols = group_keys + ["set_sort_num"]
    campaign_set = campaign_set_df[cols].drop_duplicates()
    set_cus_count = (
        campaign_set_df.groupby("set_sort_num")["cus_cd"]
        .nunique()
        .reset_index()
        .rename(columns={"cus_cd": "recipient_count"})
    )

    campaign_set_merged = campaign_set.merge(set_cus_count, on="set_sort_num", how="left")
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

    ## 그룹 변수 추가
    campaign_set_df = add_group_type(campaign_set_df)

    ## Todo: group seq 처리
    if is_personalized:
        campaign_set_df["group_sort_num"] = campaign_set_df.groupby("set_sort_num")[
            "set_group_val"
        ].transform(lambda x: pd.factorize(x)[0] + 1)
    else:
        campaign_set_df["group_sort_num"] = 1
    ## set_group 정보 : res_groups_df
    group_keys = ["set_sort_num", "group_sort_num"]
    df_grouped1 = (  # pyright: ignore [reportCallIssue]
        campaign_set_df.groupby(group_keys)[["cus_cd"]]
        .agg({"cus_cd": "nunique"})
        .rename(columns={"cus_cd": "recipient_group_count"})
    )

    if set_cus_count["recipient_count"].sum() != df_grouped1["recipient_group_count"].sum():
        raise PolicyException(
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

    # 생성에 필요한 부가정보 추가
    campaign_set_df["campaign_id"] = campaign_id
    campaign_set_df["send_result"] = None
    campaign_set_df["created_at"] = created_at
    campaign_set_df["created_by"] = user_id
    campaign_set_df["updated_at"] = created_at
    campaign_set_df["updated_by"] = user_id
    campaign_set_df = campaign_set_df.replace({np.nan: None})
    campaign_set_df = campaign_set_df.where(pd.notnull(campaign_set_df), None)

    # set_group_list 프로퍼티 값 만들기
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
                "media": media,
                "msg_type": campaign_msg_type,
                "recipient_count": row["recipient_count"],
                "group_send_count": None,
                "rep_nm": row["rep_nm"],
                "created_at": row["created_at"],
                "created_by": row["created_by"],
                "updated_at": row["updated_at"],
                "updated_by": row["updated_by"],
            }
            group_dict_list.append(elem_dict)
        campaign_set_merged.at[idx, "set_group_list"] = group_dict_list

    return campaign_set_merged, campaign_set_df
