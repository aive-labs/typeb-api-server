from abc import ABC, abstractmethod

from src.campaign.routes.dto.request.message_generate import MsgGenerationReq
from src.users.domain.user import User


class GenerateMessageUsecase(ABC):
    @abstractmethod
    def generate_message(self, message_generate: MsgGenerationReq, user: User):
        pass
