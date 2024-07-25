from sqlalchemy.orm import Session

from src.dashboard.infra.dashboard_repository import DashboardRepository


class GetAudienceStatsService:
    def __init__(self, dashboard_repository: DashboardRepository) -> None:
        self.dashboard_repository = dashboard_repository

    def get_audience_stats_options(self, db: Session, start_date, end_date):
        campaign_ids = self.dashboard_repository.get_dashboard_campaign_ids(
            db, start_date, end_date
        )
        audience_options = self.dashboard_repository.get_audience_options(
            db, start_date, end_date, campaign_ids
        )
        audience_options = sorted(audience_options, key=lambda x: x.id, reverse=True)
        return audience_options

    def get_audience_stats_result(self, db: Session, start_date, end_date, audience_id=None):
        audience_stats_df = self.dashboard_repository.get_audience_stats(db, start_date, end_date)
        audience_stats_df["strategy_theme_name"] = audience_stats_df["strategy_theme_name"].fillna(
            ""
        )
        audience_stats_df = audience_stats_df.fillna(0)
        if audience_id:
            audience_stats_df = audience_stats_df[audience_stats_df["audience_id"] == audience_id]

        audience_stats_df.sort_values(
            ["campaign_id", "audience_id"], ascending=[False, False], inplace=True
        )
        return audience_stats_df

    def get_audience_prch_item_result(self, db: Session, audience_id, start_date, end_date):
        audience_prch_item_df = self.dashboard_repository.get_audience_prch_item(
            db, audience_id, start_date, end_date
        )
        product_name_stats = (
            audience_prch_item_df.groupby(["product_name"])
            .agg(
                total_sales_count=("response_cust_count", "sum"),
                total_sales=("tot_sale_amt", "sum"),
            )
            .reset_index()
        )
        product_name_stats.loc[:, "prchs_portion"] = (
            product_name_stats["total_sales"] / product_name_stats["total_sales"].sum()
        )
        product_name_stats = product_name_stats.sort_values(by="total_sales", ascending=False)

        category_name_stats = (
            audience_prch_item_df.groupby(["category_name"])
            .agg(
                total_sales_count=("response_cust_count", "sum"),
                total_sales=("tot_sale_amt", "sum"),
            )
            .reset_index()
        )
        category_name_stats.loc[:, "prchs_portion"] = (
            category_name_stats["total_sales"] / category_name_stats["total_sales"].sum()
        )
        category_name_stats = category_name_stats.sort_values(by="total_sales", ascending=False)

        rep_nm_stats = (
            audience_prch_item_df.groupby(["rep_nm"])
            .agg(
                total_sales_count=("response_cust_count", "sum"),
                total_sales=("tot_sale_amt", "sum"),
            )
            .reset_index()
        )
        rep_nm_stats.loc[:, "prchs_portion"] = (
            rep_nm_stats["total_sales"] / rep_nm_stats["total_sales"].sum()
        )
        rep_nm_stats = rep_nm_stats.sort_values(by="total_sales", ascending=False)

        return product_name_stats, category_name_stats, rep_nm_stats
