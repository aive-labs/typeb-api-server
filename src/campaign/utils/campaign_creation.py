import numpy as np
import pandas as pd

from src.strategy.enums.recommend_model import RecommendModels


def add_group_type(set_df: pd.DataFrame):
    """그룹 구분 함수
    Case1) 개인화 모델 (recsys_model_id = 10~13)
    Case2) 연령대별 Top 추천 모델 (recsys_model_id = 9)
    Case3) Top5 추천 모델 (recsys_model_id = 1~4)
    Case4) Contents Only 추천 모델 (recsys_model_id = 6)
    Case4) 커스텀 캠페인 (recsys_model_id not in above)
    """
    personalized_model_ids = [
        item.value for item in RecommendModels if item.personalized and item.value not in [9]
    ]
    age_model_ids = [RecommendModels.GENDER_AGE_GROUP_BEST_PRODUCT_RECOMMENDATION.value]
    top_model_ids = [
        item.value for item in RecommendModels if not item.personalized and item.value not in [9]
    ]

    cond = [
        set_df["recsys_model_id"].isin(personalized_model_ids),
        set_df["recsys_model_id"].isin(age_model_ids),
        set_df["recsys_model_id"].isin(top_model_ids),
        ~set_df["recsys_model_id"].isin(personalized_model_ids + age_model_ids + top_model_ids),
    ]

    choice = [
        set_df["purpose_lv2"],
        set_df["age_lv1"],
        set_df["purpose_lv1"],  ## 추천 대표상품으로 나뉘어야 함 (REP_NM)
        set_df["purpose_lv1"],
        set_df["purpose_lv1"],
    ]

    choice_category = ["purpose_lv2", "age", "rep_nm", "purpose", "purpose"]

    set_df["set_group_category"] = np.select(cond, choice_category)
    set_df["set_group_val"] = np.select(cond, choice)  # item_group_type
    return set_df
