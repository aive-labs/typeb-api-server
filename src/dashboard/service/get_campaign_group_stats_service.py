import numpy as np
from sqlalchemy.orm import Session

from src.dashboard.infra.dashboard_repository import DashboardRepository


class GetCampaignGroupStatsService:
    def __init__(self, dashboard_repository: DashboardRepository) -> None:
        self.dashboard_repository = dashboard_repository
        self.code_dict = {
            "audience_name": "타겟 오디언스",
            "group_sort_num": "그룹",
            "cus_grade1_nm": "멤버십 등급",
            "age_group_10": "연령대",
            "cv_lv2": "CV",
        }

    def get_campaign_group_stats_codes(self):
        return self.code_dict

    def get_campaign_group_stats_result(
        self, db: Session, start_date, end_date, group_code_lv1=None, group_code_lv2=None
    ):
        campaign_ids = self.dashboard_repository.get_dashboard_campaign_ids(
            db, start_date, end_date
        )
        campaign_group_stats = self.dashboard_repository.get_campaign_group_stats(
            db, start_date, end_date, campaign_ids, group_code_lv1, group_code_lv2
        )

        campaign_group_stats.sort_values("campaign_id", ascending=False, inplace=True)
        campaign_group_stats.replace({np.nan: None}, inplace=True)
        campaign_lst_df = campaign_group_stats[["campaign_id", "campaign_name"]].drop_duplicates(
            keep="first"
        )
        campaign_lst_df.sort_values("campaign_id", ascending=False, inplace=True)

        return campaign_group_stats, campaign_lst_df
