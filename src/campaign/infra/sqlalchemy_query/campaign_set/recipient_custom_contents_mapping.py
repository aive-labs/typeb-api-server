from sqlalchemy.orm import Session

from src.campaign.infra.sqlalchemy_query.get_contents_from_strategy import (
    get_contents_from_strategy,
)
from src.campaign.infra.sqlalchemy_query.get_contents_name_with_rep_nm import (
    get_contents_name_with_rep_nm,
)
from src.common.utils.data_converter import DataConverter


def recipient_custom_contents_mapping(campaign_set_df, selected_themes, db: Session):
    """전략에서 선택된 추천 콘텐츠의 아이디를 조인하여 정보를 매핑"""
    theme_contents = get_contents_from_strategy(selected_themes, db)
    theme_contents_df = DataConverter.convert_query_to_df(theme_contents)

    contents_info = get_contents_name_with_rep_nm(db)
    contents_info_df = DataConverter.convert_query_to_df(contents_info)

    theme_contents_df["strategy_theme_id"] = theme_contents_df["strategy_theme_id"].astype(int)
    theme_contents_df["contents_id"] = theme_contents_df["contents_id"].astype(str)
    contents_info_df["contents_id"] = contents_info_df["contents_id"].astype(str)

    campaign_set_df = campaign_set_df.merge(theme_contents_df, on="strategy_theme_id", how="left")
    campaign_set_df = campaign_set_df.merge(contents_info_df, on="contents_id", how="left")

    # contents_info_df와 contents_id로 조인되는 키가 없는 경우, 아래 로직이 실행 안됨
    if "rep_nm_x" in campaign_set_df.columns:
        campaign_set_df = campaign_set_df.drop(columns=["rep_nm_x"])

    if "rep_nm_y" in campaign_set_df.columns:
        campaign_set_df = campaign_set_df.rename(columns={"rep_nm_y": "rep_nm"})

    return campaign_set_df
