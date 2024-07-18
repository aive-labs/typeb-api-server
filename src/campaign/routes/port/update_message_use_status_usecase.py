from abc import ABC, abstractmethod

from src.core.transactional import transactional


class UpdateMessageUseStatusUseCase(ABC):

    @transactional
    @abstractmethod
    def exec(self, campaign_id, set_group_msg_seq, is_used_obj, user, db):
        pass
