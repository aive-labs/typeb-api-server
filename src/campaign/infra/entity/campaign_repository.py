from src.campaign.infra.campaign_sqlalchemy_repository import CampaignSqlAlchemy
from src.campaign.service.port.base_campaign_repository import BaseCampaignRepository
from src.users.domain.user import User


class CampaignRepository(BaseCampaignRepository):

    def __init__(self, campaign_sqlalchemy: CampaignSqlAlchemy):
        self.campagin_sqlalchemy = campaign_sqlalchemy

    def create_campaign():
        raise NotImplementedError

    def get_campaigns(self, start_date: str, end_date: str, user: User):
        self.campagin_sqlalchemy.get_all_campaigns(start_date, end_date, user)
        raise NotImplementedError

    def is_existing_campaign_by_name(self, name: str) -> bool:
        campaign_entity = self.campagin_sqlalchemy.get_campaign_by_name(name)

        if campaign_entity:
            return True

        return False
