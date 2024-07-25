from sqlalchemy.orm import Session

from src.dashboard.infra.dashboard_sqlalchemy_repository import DashboardSqlAlchemy
from src.dashboard.service.port.base_dashboard_repository import BaseDashboardRepository


class DashboardRepository(BaseDashboardRepository):

    def __init__(self, dashboard_sqlalchemy: DashboardSqlAlchemy):
        self.dashboard_sqlalchemy = dashboard_sqlalchemy

    def get_dashboard_campaign_ids(self, db: Session, start_date, end_date):
        return self.dashboard_sqlalchemy.get_dashboard_campaign_ids(db, start_date, end_date)

    def get_campaign_stats(self, db: Session, start_date, end_date, campaign_ids):
        return self.dashboard_sqlalchemy.get_campaign_stats(db, start_date, end_date, campaign_ids)

    def get_campaign_group_stats(
        self,
        db: Session,
        start_date,
        end_date,
        campaign_ids,
        group_code_lv1=None,
        group_code_lv2=None,
    ):
        return self.dashboard_sqlalchemy.get_campaign_group_stats(
            db, start_date, end_date, campaign_ids, group_code_lv1, group_code_lv2
        )

    def get_audience_options(self, db: Session, start_date, end_date, campaign_ids):
        return self.dashboard_sqlalchemy.get_audience_options(
            db, start_date, end_date, campaign_ids
        )

    def get_audience_stats(self, db: Session, start_date, end_date):
        return self.dashboard_sqlalchemy.get_audience_stats(db, start_date, end_date)

    def get_audience_prch_item(self, db: Session, audience_id, start_date, end_date):
        return self.dashboard_sqlalchemy.get_audience_prch_item(
            db, audience_id, start_date, end_date
        )
