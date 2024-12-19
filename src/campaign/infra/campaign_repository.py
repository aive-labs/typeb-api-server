from sqlalchemy.orm import Session

from src.campaign.domain.campaign import Campaign
from src.campaign.domain.campaign_messages import SetGroupMessage
from src.campaign.domain.campaign_remind import CampaignRemind
from src.campaign.domain.campaign_timeline import CampaignTimeline
from src.campaign.domain.send_reservation import SendReservation
from src.campaign.infra.campaign_sqlalchemy_repository import CampaignSqlAlchemy
from src.campaign.infra.dto.already_sent_campaign import AlreadySentCampaign
from src.campaign.infra.dto.campaign_reviewer_info import CampaignReviewerInfo
from src.campaign.model.campaign_progress import CampaignProgress
from src.campaign.service.port.base_campaign_repository import BaseCampaignRepository
from src.search.model.id_with_item_response import IdWithItem
from src.user.domain.user import User


class CampaignRepository(BaseCampaignRepository):

    def __init__(self, campaign_sqlalchemy: CampaignSqlAlchemy):
        self.campaign_sqlalchemy = campaign_sqlalchemy

    def create_campaign(self, new_campaign: Campaign, db: Session) -> Campaign:
        return self.campaign_sqlalchemy.register_campaign(new_campaign, db)

    def get_campaigns(
        self, start_date: str, end_date: str, user: User, db: Session
    ) -> list[Campaign]:
        return self.campaign_sqlalchemy.get_all_campaigns(start_date, end_date, user, db)

    def is_existing_campaign_by_name(self, name: str, db: Session) -> bool:
        campaign_entity = self.campaign_sqlalchemy.get_campaign_by_name(name, db)

        if campaign_entity:
            return True

        return False

    def get_campaign_by_strategy_id(self, strategy_id: str, db: Session) -> list[Campaign]:
        campaigns = self.campaign_sqlalchemy.get_campaign_by_strategy_id(strategy_id, db)
        return campaigns

    def is_existing_campaign_by_offer_event_no(self, offer_event_no: str, db: Session) -> bool:
        return self.campaign_sqlalchemy.is_existing_campaign_by_offer_event_no(offer_event_no, db)

    def get_timeline(self, campaign_id: str, db: Session) -> list[CampaignTimeline]:
        return self.campaign_sqlalchemy.get_timeline(campaign_id, db)

    def search_campaign(self, keyword, current_date, two_weeks_ago, db) -> list[IdWithItem]:
        return self.campaign_sqlalchemy.search_campaign(keyword, current_date, two_weeks_ago, db)

    def get_send_complete_campaign(
        self, campaign_id: str, req_set_group_seqs: list, db: Session
    ) -> SendReservation:
        return self.campaign_sqlalchemy.get_send_complete_campaign(
            campaign_id, req_set_group_seqs, db
        )

    def get_group_item_nm_stats(self, campaign_id: str, set_sort_num: int, db: Session):
        return self.campaign_sqlalchemy.get_group_item_nm_stats(campaign_id, set_sort_num, db)

    def get_it_gb_nm_stats(self, campaign_id: str, set_sort_num: int, db: Session):
        return self.campaign_sqlalchemy.get_it_gb_nm_stats(campaign_id, set_sort_num, db)

    def get_age_stats(self, campaign_id: str, set_sort_num: int, db: Session):
        return self.campaign_sqlalchemy.get_age_stats(campaign_id, set_sort_num, db)

    def get_campaign_messages(self, campaign_id: str, req_set_group_seqs: list, db: Session):  ###
        return self.campaign_sqlalchemy.get_campaign_messages(campaign_id, req_set_group_seqs, db)

    def save_timeline(self, timeline: CampaignTimeline, db: Session):
        return self.campaign_sqlalchemy.save_timeline(timeline, db)

    def get_campaign_detail(self, campaign_id, user, db: Session) -> Campaign:
        return self.campaign_sqlalchemy.get_campaign_detail(campaign_id, user, db)

    def get_campaign_remind(self, campaign_id: str, db: Session) -> list[CampaignRemind]:
        return self.campaign_sqlalchemy.get_campaign_remind(campaign_id, db)

    def get_campaign_reviewers(self, campaign_id: str, db: Session) -> list[CampaignReviewerInfo]:
        return self.campaign_sqlalchemy.get_campaign_reviewers(campaign_id, db)

    def update_campaign_progress_status(
        self, campaign_id: str, update_status: CampaignProgress, db: Session
    ):
        return self.campaign_sqlalchemy.update_campaign_progress_status(
            campaign_id, update_status.value, db
        )

    def get_campaign_set_group_message(
        self, campaign_id: str, set_group_msg_seq: int, db: Session
    ) -> SetGroupMessage:
        return self.campaign_sqlalchemy.get_campaign_set_group_message(
            campaign_id, set_group_msg_seq, db
        )

    def get_message_in_send_reservation(
        self, campaign_id, set_group_msg_seq, db: Session
    ) -> SendReservation | None:
        return self.campaign_sqlalchemy.get_message_in_send_reservation(
            campaign_id, set_group_msg_seq, db
        )

    def update_campaign_set_group_message_type(
        self, campaign_id, set_group_seq, message_type, db: Session
    ):
        self.campaign_sqlalchemy.update_campaign_set_group_message_type(
            campaign_id, set_group_seq, message_type, db
        )

    def delete_campaign(self, campaign, db: Session):
        self.campaign_sqlalchemy.delete_campaign(campaign, db)

    def update_send_reservation_status_to_success(self, refkey, db: Session):
        self.campaign_sqlalchemy.update_send_reservation_status_to_success(refkey, db)

    def update_send_reservation_status_to_failure(self, refkey: str, db: Session):
        self.campaign_sqlalchemy.update_send_reservation_status_to_failure(refkey, db)

    def get_already_sent_campaigns(self, campaign_id, db: Session) -> list[AlreadySentCampaign]:
        return self.campaign_sqlalchemy.get_already_sent_campaigns(campaign_id, db)
