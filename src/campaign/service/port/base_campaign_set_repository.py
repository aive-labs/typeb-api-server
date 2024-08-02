from abc import ABC, abstractmethod

from sqlalchemy.orm import Session

from src.campaign.domain.campaign import Campaign
from src.campaign.domain.campaign_messages import MessageResource, SetGroupMessage


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
    def update_message_confirm_status(self, campaign_id, set_seq, is_confirmed, db: Session):
        pass

    @abstractmethod
    def get_campaign_set_group_message_by_msg_seq(
        self, campaign_id, set_group_msg_seq, db
    ) -> SetGroupMessage:
        pass

    @abstractmethod
    def update_use_status(self, campaign_id, set_group_msg_seq, is_used, db: Session):
        pass

    @abstractmethod
    def update_status_to_confirmed(self, campaign_id, set_seq, db: Session):
        pass

    @abstractmethod
    def update_all_sets_status_to_confirmed(self, campaign_id, db: Session):
        pass

    @abstractmethod
    def get_campaign_info_for_summary(self, campaign_id, db: Session):
        pass

    @abstractmethod
    def get_campaign_set_group_messages_in_use(self, campaign_id, db) -> list[SetGroupMessage]:
        pass

    @abstractmethod
    def get_set_group_message(self, campaign_id, set_group_msg_seq, db: Session) -> SetGroupMessage:
        pass

    @abstractmethod
    def update_message_image(
        self, campaign_id, set_group_msg_seq, message_photo_uri: list[str], db: Session
    ):
        pass

    @abstractmethod
    def get_message_image_source(self, set_group_msg_seq, db: Session) -> MessageResource:
        pass

    @abstractmethod
    def delete_message_image_source(self, set_group_msg_seq, db: Session):
        pass

    @abstractmethod
    def delete_msg_photo_uri_by_set_group_msg_req(self, set_group_msg_seq, db: Session):
        pass
