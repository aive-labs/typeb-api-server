from src.messages.infra.ppurio_message_repository import PpurioMessageRepository
from src.messages.routes.dto.ppurio_message_result import PpurioMessageResult


class MessageService:

    def __init__(self, message_repository: PpurioMessageRepository):
        self.message_repository = message_repository

    def save_message_result(self, ppurio_message_result: PpurioMessageResult):
        self.message_repository.save_message_result(ppurio_message_result)
