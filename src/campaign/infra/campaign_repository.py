from sqlalchemy.orm import Session

from src.campaign.domain.campaign import Campaign
from src.campaign.domain.campaign_timeline import CampaignTimeline
from src.campaign.domain.send_reservation import SendReservation
from src.campaign.infra.campaign_sqlalchemy_repository import CampaignSqlAlchemy
from src.campaign.service.port.base_campaign_repository import BaseCampaignRepository
from src.search.routes.dto.id_with_item_response import IdWithItem
from src.users.domain.user import User


class CampaignRepository(BaseCampaignRepository):

    def __init__(self, campaign_sqlalchemy: CampaignSqlAlchemy):
        self.campaign_sqlalchemy = campaign_sqlalchemy

    def create_campaign():
        raise NotImplementedError

    def get_campaigns(
        self, start_date: str, end_date: str, user: User
    ) -> list[Campaign]:
        return self.campaign_sqlalchemy.get_all_campaigns(start_date, end_date, user)

    def is_existing_campaign_by_name(self, name: str) -> bool:
        campaign_entity = self.campaign_sqlalchemy.get_campaign_by_name(name)

        if campaign_entity:
            return True

        return False

    def get_campaign_by_strategy_id(
        self, strategy_id: str, db: Session
    ) -> list[Campaign]:
        campaigns = self.campaign_sqlalchemy.get_campaign_by_strategy_id(
            strategy_id, db
        )
        return campaigns

    def is_existing_campaign_by_offer_event_no(self, offer_event_no: str) -> bool:
        return self.campaign_sqlalchemy.is_existing_campaign_by_offer_event_no(
            offer_event_no
        )

    def get_timeline(self, campaign_id: str, db: Session) -> list[CampaignTimeline]:
        return self.campaign_sqlalchemy.get_timeline(campaign_id, db)

    def search_campaign(
        self, keyword, current_date, two_weeks_ago, db
    ) -> list[IdWithItem]:
        return self.campaign_sqlalchemy.search_campaign(
            keyword, current_date, two_weeks_ago, db
        )

    def get_send_complete_campaign(
        self, campaign_id: str, req_set_group_seqs: list, db: Session
    ) -> SendReservation:
        return self.campaign_sqlalchemy.get_send_complete_campaign(
            campaign_id, req_set_group_seqs, db
        )

    def get_group_item_nm_stats(self, campaign_id: str, set_sort_num: int):  ###
        return self.campaign_sqlalchemy.get_group_item_nm_stats(
            campaign_id, set_sort_num
        )

    def get_it_gb_nm_stats(self, campaign_id: str, set_sort_num: int):  ###
        return self.campaign_sqlalchemy.get_it_gb_nm_stats(campaign_id, set_sort_num)

    def get_age_stats(self, campaign_id: str, set_sort_num: int):  ###
        return self.campaign_sqlalchemy.get_age_stats(campaign_id, set_sort_num)

    def get_campaign_messages(self, campaign_id: str, req_set_group_seqs: list):  ###
        return self.campaign_sqlalchemy.get_campaign_messages(
            campaign_id, req_set_group_seqs
        )
