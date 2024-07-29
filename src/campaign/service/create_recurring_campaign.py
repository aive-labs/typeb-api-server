from sqlalchemy.orm import Session

from src.campaign.routes.port.create_recurring_campaign_usecase import (
    CreateRecurringCampaignUseCase,
)
from src.campaign.service.port.base_campaign_repository import BaseCampaignRepository
from src.campaign.service.port.base_campaign_set_repository import (
    BaseCampaignSetRepository,
)
from src.core.transactional import transactional
from src.users.domain.user import User


class CreateRecurringCampaign(CreateRecurringCampaignUseCase):

    def __init__(
        self,
        campaign_repository: BaseCampaignRepository,
        campaign_set_repository: BaseCampaignSetRepository,
    ):
        self.campaign_repository = campaign_repository
        self.campaign_set_repository = campaign_set_repository

    @transactional
    def exec(self, campaign_id, user: User, db: Session):
        pass
