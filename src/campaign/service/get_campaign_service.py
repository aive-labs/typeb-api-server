from src.campaign.domain.campaign import Campaign
from src.campaign.routes.port.get_campaign_usecase import GetCampaignUsecase
from src.campaign.service.port.base_campaign_repository import BaseCampaignRepository
from src.users.domain.user import User


class GetCampaignService(GetCampaignUsecase):

    def __init__(self, campaign_repository: BaseCampaignRepository):
        self.campaign_repository = campaign_repository

    def get_campaigns(
        self, start_date: str, end_date: str, user: User
    ) -> list[Campaign]:
        campaigns = self.campaign_repository.get_campaigns(start_date, end_date)
        return campaigns
