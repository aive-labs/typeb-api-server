from abc import ABC, abstractmethod

from src.campaign.domain.campaign import Campaign


class BaseCampaignRepository(ABC):

    @abstractmethod
    def create_campaign():
        pass

    @abstractmethod
    def get_campaigns(self, start_date: str, end_date: str) -> list[Campaign]:
        pass

    @abstractmethod
    def is_existing_campaign_by_name(self, name: str) -> bool:
        pass
