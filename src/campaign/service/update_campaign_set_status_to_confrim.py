from sqlalchemy.orm import Session

from src.campaign.routes.port.update_campaign_set_confirm_usecase import (
    UpdateCampaignSetStatusToConfirmUseCase,
)
from src.campaign.service.port.base_campaign_repository import BaseCampaignRepository
from src.campaign.service.port.base_campaign_set_repository import (
    BaseCampaignSetRepository,
)
from src.core.transactional import transactional


class UpdateCampaignStatusToConfirm(UpdateCampaignSetStatusToConfirmUseCase):

    def __init__(
        self,
        campaign_repository: BaseCampaignRepository,
        campaign_set_repository: BaseCampaignSetRepository,
    ):
        self.campaign_repository = campaign_repository
        self.campaign_set_repository = campaign_set_repository

    @transactional
    def campaign_set_status_to_confirm(self, campaign_id: str, set_seq: int, db: Session):
        self.campaign_set_repository.update_status_to_confirmed(campaign_id, set_seq, db)

    @transactional
    def all_campaign_set_status_to_confirm(self, campaign_id: str, db: Session):
        self.campaign_set_repository.update_all_sets_status_to_confirmed(campaign_id, db)
