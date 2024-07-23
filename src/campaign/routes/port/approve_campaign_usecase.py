from abc import ABC, abstractmethod

from src.campaign.service.port.base_campaign_repository import BaseCampaignRepository
from src.campaign.service.port.base_campaign_set_repository import (
    BaseCampaignSetRepository,
)


class ApproveCampaignUseCase(ABC):
    def __init__(
        self,
        campaign_repository: BaseCampaignRepository,
        campaign_set_repository: BaseCampaignSetRepository,
    ):
        self.campaign_repository = campaign_repository
        self.campaign_set_repository = campaign_set_repository

    @abstractmethod
    def exec(self, campaign_id, to_status, db, user, background_task, reviewers=None):
        pass
