from abc import ABC, abstractmethod

import pandas as pd
from sqlalchemy.orm import Session


class BaseDashboardRepository(ABC):

    @abstractmethod
    def get_dashboard_campaign_ids(self, db: Session, start_date, end_date) -> pd.DataFrame:
        pass

    @abstractmethod
    def get_campaign_stats(self, db: Session, start_date, end_date, campaign_ids) -> pd.DataFrame:
        pass

    @abstractmethod
    def get_campaign_group_stats(
        self,
        db: Session,
        start_date,
        end_date,
        campaign_ids,
        group_code_lv1=None,
        group_code_lv2=None,
    ) -> pd.DataFrame:
        pass

    @abstractmethod
    def get_audience_options(self, db: Session, start_date, end_date, campaign_ids) -> pd.DataFrame:
        pass

    @abstractmethod
    def get_audience_stats(self, db: Session, start_date, end_date) -> pd.DataFrame:
        pass

    @abstractmethod
    def get_audience_prch_item(
        self, db: Session, audience_id, start_date, end_date
    ) -> pd.DataFrame:
        pass
