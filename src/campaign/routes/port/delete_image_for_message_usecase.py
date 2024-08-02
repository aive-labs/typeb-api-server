from abc import ABC, abstractmethod

from sqlalchemy.orm import Session

from src.campaign.routes.dto.response.set_group_seq_with_message_response import (
    SetGroupSeqWithMessageResponse,
)


class DeleteImageForMessageUseCase(ABC):

    @abstractmethod
    async def exec(
        self, campaign_id: str, set_group_msg_seq, user, db: Session
    ) -> SetGroupSeqWithMessageResponse:
        pass
