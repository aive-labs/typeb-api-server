from abc import ABC, abstractmethod

from sqlalchemy.orm import Session

from src.main.transactional import transactional


class ConfirmCampaignSetGroupMessageUseCase(ABC):

    @transactional
    @abstractmethod
    def exec(self, campaign_id, set_seq, is_confirmed_obj, user, db: Session):
        pass
