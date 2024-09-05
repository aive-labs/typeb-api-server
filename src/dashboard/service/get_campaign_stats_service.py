import numpy as np
from sqlalchemy.orm import Session

from src.dashboard.infra.dashboard_repository import DashboardRepository


class GetCampaignStatsService:
    def __init__(self, dashboard_repository: DashboardRepository) -> None:
        self.dashboard_repository = dashboard_repository

    def get_campaign_stats_result(self, db: Session, start_date, end_date):
        campaign_ids = self.dashboard_repository.get_dashboard_campaign_ids(
            db, start_date, end_date
        )
        campaign_stats_df = self.dashboard_repository.get_campaign_stats(
            db, start_date, end_date, campaign_ids
        )

        campaign_summary_stats_df = (
            campaign_stats_df.groupby(["campaign_id"])
            .agg(
                campaign_name=("campaign_name", "max"),
                start_date=("start_date", "max"),
                end_date=("end_date", "max"),
                campaign_status_name=("campaign_status_name", "max"),
                recipient_count=("recipient_count", "sum"),
                sent_cust_count=("sent_cust_count", "sum"),
                media_cost=("media_cost", "sum"),
                response_cust_count=("response_cust_count", "sum"),
                response_quantity=("response_quantity", "sum"),
                response_revenue=("response_revenue", "sum"),
                response_unit_price=("response_unit_price", "mean"),
                response_roi=("response_roi", "mean"),
                e_response_cust_count=("e_response_cust_count", "sum"),
                e_response_quantity=("e_response_quantity", "sum"),
                e_response_revenue=("e_response_revenue", "sum"),
                e_response_unit_price=("e_response_unit_price", "mean"),
            )
            .reset_index()
        )

        if len(campaign_stats_df) > 0:
            campaign_summary_stats_df.replace({np.nan: None}, inplace=True)
            campaign_summary_stats_df["response_rate"] = (
                campaign_summary_stats_df.response_cust_count
                / campaign_summary_stats_df.recipient_count
            )
            campaign_summary_stats_df["e_response_rate"] = (
                campaign_summary_stats_df.e_response_cust_count
                / campaign_summary_stats_df.recipient_count
            )

            campaign_summary_stats_df.response_unit_price = campaign_summary_stats_df[
                ["response_revenue", "response_cust_count"]
            ].apply(
                lambda x: (
                    int(x["response_revenue"] / x["response_cust_count"])
                    if x["response_cust_count"] > 0
                    else 0
                ),
                axis=1,
            )
            campaign_summary_stats_df.e_response_unit_price = campaign_summary_stats_df[
                ["e_response_revenue", "e_response_cust_count"]
            ].apply(
                lambda x: (
                    int(x["e_response_revenue"] / x["e_response_cust_count"])
                    if x["e_response_cust_count"] > 0
                    else 0
                ),
                axis=1,
            )
            campaign_summary_stats_df.response_unit_price = (
                campaign_summary_stats_df.response_unit_price.apply(
                    lambda x: int(x) if x != None else x
                )
            )
            campaign_summary_stats_df.e_response_unit_price = (
                campaign_summary_stats_df.e_response_unit_price.apply(
                    lambda x: int(x) if x != None else x
                )
            )

            campaign_stats_df.replace({np.nan: None}, inplace=True)
            campaign_stats_df.response_unit_price = campaign_stats_df.response_unit_price.apply(
                lambda x: int(x) if x != None else x
            )
            campaign_stats_df.e_response_unit_price = campaign_stats_df.e_response_unit_price.apply(
                lambda x: int(x) if x != None else x
            )

            campaign_summary_stats_df.replace({np.nan: None}, inplace=True)
            campaign_stats_df.replace({np.nan: None}, inplace=True)
            campaign_stats_df["strategy_theme_name"] = campaign_stats_df[
                "strategy_theme_name"
            ].fillna("")

        del campaign_stats_df["start_date"]
        del campaign_stats_df["end_date"]
        del campaign_stats_df["campaign_status_name"]

        return campaign_summary_stats_df, campaign_stats_df
