from abc import ABC, abstractmethod

from sqlalchemy.orm import Session

from src.campaign.domain.campaign import Campaign
from src.campaign.domain.campaign_timeline import CampaignTimeline
from src.search.routes.dto.id_with_item_response import IdWithItem
from src.users.domain.user import User


class BaseCampaignRepository(ABC):
    @abstractmethod
    def create_campaign(self, new_campaign: Campaign, db: Session) -> Campaign:
        pass

    @abstractmethod
    def get_campaigns(self, start_date: str, end_date: str, user: User) -> list[Campaign]:
        pass

    @abstractmethod
    def is_existing_campaign_by_name(self, name: str) -> bool:
        pass

    @abstractmethod
    def is_existing_campaign_by_offer_event_no(self, offer_event_no: str) -> bool:
        pass

    @abstractmethod
    def get_campaign_by_strategy_id(self, strategy_id: str, db: Session) -> list[Campaign]:
        pass

    @abstractmethod
    def get_timeline(self, campaign_id: str, db: Session) -> list[CampaignTimeline]:
        pass

    @abstractmethod
    def search_campaign(self, keyword, current_date, two_weeks_ago, db) -> list[IdWithItem]:
        pass

    @abstractmethod
    def save_timeline(self, timeline: CampaignTimeline, db: Session):
        pass
