from abc import ABC, abstractmethod

from sqlalchemy.orm import Session

from src.core.transactional import transactional


class UpdateCampaignSetStatusToConfirmUseCase(ABC):

    @transactional
    @abstractmethod
    def campaign_set_status_to_confirm(self, campaign_id: str, set_seq: int, db: Session):
        pass

    @transactional
    @abstractmethod
    def all_campaign_set_status_to_confirm(self, campaign_id: str, db: Session):
        pass
