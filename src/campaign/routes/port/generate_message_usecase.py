from abc import ABC, abstractmethod

from sqlalchemy.orm import Session

from src.campaign.routes.dto.request.message_generate import MsgGenerationReq
from src.campaign.routes.dto.response.generate_message_response import GeneratedMessage
from src.strategy.routes.dto.request.preview_message_create import PreviewMessageCreate
from src.strategy.routes.dto.response.preview_message_response import (
    PreviewMessageResponse,
)
from src.user.domain.user import User


class GenerateMessageUsecase(ABC):
    @abstractmethod
    def generate_message(
        self, message_generate: MsgGenerationReq, user: User, db: Session
    ) -> list[GeneratedMessage]:
        pass

    @abstractmethod
    def generate_preview_message(
        self, preview_message_create: PreviewMessageCreate, user: User, db: Session
    ) -> PreviewMessageResponse:
        pass
