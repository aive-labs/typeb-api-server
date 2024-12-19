from sqlalchemy.orm import Session

from src.campaign.enums.campaign_progress import CampaignProgress
from src.campaign.routes.port.update_campaign_progress_usecase import (
    UpdateCampaignProgressUseCase,
)
from src.campaign.service.port.base_campaign_repository import BaseCampaignRepository
from src.main.transactional import transactional


class UpdateCampaignProgressService(UpdateCampaignProgressUseCase):

    def __init__(self, campaign_repository: BaseCampaignRepository):
        self.campaign_repository = campaign_repository

    @transactional
    def exec(self, campaign_id: str, update_status: CampaignProgress, db: Session):
        self.campaign_repository.update_campaign_progress_status(campaign_id, update_status, db)
