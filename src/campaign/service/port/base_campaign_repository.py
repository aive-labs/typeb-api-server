from abc import ABC, abstractmethod

from sqlalchemy.orm import Session

from src.campaign.domain.campaign import Campaign
from src.users.domain.user import User


class BaseCampaignRepository(ABC):
    @abstractmethod
    def create_campaign():
        pass

    @abstractmethod
    def get_campaigns(
        self, start_date: str, end_date: str, user: User
    ) -> list[Campaign]:
        pass

    @abstractmethod
    def is_existing_campaign_by_name(self, name: str) -> bool:
        pass

    @abstractmethod
    def is_existing_campaign_by_offer_event_no(self, offer_event_no: str) -> bool:
        pass

    @abstractmethod
    def get_campaign_by_strategy_id(
        self, strategy_id: str, db: Session
    ) -> list[Campaign]:
        pass
