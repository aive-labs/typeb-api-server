from abc import ABC, abstractmethod

from fastapi import UploadFile

from src.core.transactional import transactional


class CampaignMessageImageUploadUseCase(ABC):

    @transactional
    @abstractmethod
    def exec(self, campaign_id, set_group_msg_seq, files: list[UploadFile]):
        pass
