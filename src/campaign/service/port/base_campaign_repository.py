from abc import ABC, abstractmethod

from sqlalchemy.orm import Session

from src.campaign.domain.campaign import Campaign
from src.campaign.domain.campaign_messages import SetGroupMessage
from src.campaign.domain.campaign_remind import CampaignRemind
from src.campaign.domain.campaign_timeline import CampaignTimeline
from src.campaign.domain.send_reservation import SendReservation
from src.campaign.enums.campaign_progress import CampaignProgress
from src.campaign.infra.dto.already_sent_campaign import AlreadySentCampaign
from src.campaign.infra.dto.campaign_reviewer_info import CampaignReviewerInfo
from src.search.routes.dto.id_with_item_response import IdWithItem
from src.users.domain.user import User


class BaseCampaignRepository(ABC):
    @abstractmethod
    def create_campaign(self, new_campaign: Campaign, db: Session) -> Campaign:
        pass

    @abstractmethod
    def get_campaigns(
        self, start_date: str, end_date: str, user: User, db: Session
    ) -> list[Campaign]:
        pass

    @abstractmethod
    def is_existing_campaign_by_name(self, name: str, db: Session) -> bool:
        pass

    @abstractmethod
    def is_existing_campaign_by_offer_event_no(self, offer_event_no: str, db: Session) -> bool:
        pass

    @abstractmethod
    def get_campaign_by_strategy_id(self, strategy_id: str, db: Session) -> list[Campaign]:
        pass

    @abstractmethod
    def get_timeline(self, campaign_id: str, db: Session) -> list[CampaignTimeline]:
        pass

    @abstractmethod
    def search_campaign(
        self, keyword, current_date, two_weeks_ago, db: Session
    ) -> list[IdWithItem]:
        pass

    @abstractmethod
    def save_timeline(self, timeline: CampaignTimeline, db: Session):
        pass

    @abstractmethod
    def get_campaign_detail(self, campaign_id, user, db: Session) -> Campaign:
        pass

    @abstractmethod
    def get_campaign_remind(self, campaign_id: str, db: Session) -> list[CampaignRemind]:
        pass

    @abstractmethod
    def get_campaign_reviewers(self, campaign_id: str, db: Session) -> list[CampaignReviewerInfo]:
        pass

    @abstractmethod
    def update_campaign_progress_status(
        self, campaign_id: str, update_status: CampaignProgress, db: Session
    ):
        pass

    @abstractmethod
    def get_campaign_set_group_message(
        self, campaign_id: str, set_group_msg_seq: int, db: Session
    ) -> SetGroupMessage:
        pass

    @abstractmethod
    def get_message_in_send_reservation(
        self, campaign_id, set_group_msg_seq, db: Session
    ) -> SendReservation | None:
        pass

    @abstractmethod
    def update_campaign_set_group_message_type(
        self, campaign_id, set_group_seq, message_type, db: Session
    ):
        pass

    @abstractmethod
    def delete_campaign(self, campaign, db: Session):
        pass

    @abstractmethod
    def update_send_reservation_status_to_success(self, refkey: str, db: Session):
        pass

    @abstractmethod
    def update_send_reservation_status_to_failure(self, refkey: str, db: Session):
        pass

    @abstractmethod
    def get_already_sent_campaigns(self, campaign_id, db: Session) -> list[AlreadySentCampaign]:
        pass

    @abstractmethod
    def get_campaign_messages(self, campaign_id: str, req_set_group_seqs: list, db: Session):  ###
        pass

    @abstractmethod
    def get_group_item_nm_stats(self, campaign_id: str, set_sort_num: int, db: Session):
        pass

    @abstractmethod
    def get_it_gb_nm_stats(self, campaign_id: str, set_sort_num: int, db: Session):
        pass

    @abstractmethod
    def get_age_stats(self, campaign_id: str, set_sort_num: int, db: Session):
        pass
