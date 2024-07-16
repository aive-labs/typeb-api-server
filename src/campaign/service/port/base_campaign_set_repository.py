from abc import ABC, abstractmethod

from sqlalchemy.orm import Session

from src.campaign.domain.campaign import Campaign


class BaseCampaignSetRepository(ABC):
    @abstractmethod
    def create_campaign_set(self, campaign: Campaign, user_id: str, db: Session) -> tuple:
        pass

    @abstractmethod
    def get_campaign_set_group_messages(self, campaign_id: str, db: Session) -> list:
        pass

    @abstractmethod
    def get_set_portion(self, campaign_id: str, db: Session) -> tuple:
        pass

    @abstractmethod
    def get_audience_ids(self, campaign_id: str, db: Session) -> list[str]:
        pass
