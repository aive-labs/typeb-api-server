from sqlalchemy.orm import Session

from src.campaign.domain.campaign import Campaign
from src.campaign.infra.campaign_sqlalchemy_repository import CampaignSqlAlchemy
from src.campaign.service.port.base_campaign_repository import BaseCampaignRepository
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
