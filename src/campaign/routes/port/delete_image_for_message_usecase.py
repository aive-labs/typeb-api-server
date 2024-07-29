from abc import ABC, abstractmethod

from sqlalchemy.orm import Session


class DeleteImageForMessageUseCase(ABC):

    @abstractmethod
    async def exec(self, campaign_id: str, set_group_msg_seq, user, db: Session):
        pass
