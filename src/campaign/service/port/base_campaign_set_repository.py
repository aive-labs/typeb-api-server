from abc import ABC, abstractmethod

from sqlalchemy.orm import Session

from src.campaign.domain.campaign import Campaign
from src.campaign.domain.campaign_messages import SetGroupMessage


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

    @abstractmethod
    def get_campaign_set_group(self, campaign_id, set_seq, db: Session) -> list[SetGroupMessage]:
        pass

    @abstractmethod
    def update_confirm_status(self, campaign_id, set_seq, is_confirmed, db: Session):
        pass

    @abstractmethod
    def get_campaign_set_group_message_by_msg_seq(
        self, campaign_id, set_group_msg_seq, db
    ) -> SetGroupMessage:
        pass

    @abstractmethod
    def update_use_status(self, campaign_id, set_group_msg_seq, is_used, db: Session):
        pass
