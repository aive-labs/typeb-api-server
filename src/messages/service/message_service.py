from src.messages.infra.ppurio_message_repository import PpurioMessageRepository
from src.messages.routes.dto.ppurio_message_result import PpurioMessageResult


class MessageService:

    def __init__(self, message_repository: PpurioMessageRepository):
        self.message_repository = message_repository

    def save_message_result(self, ppurio_message_result: PpurioMessageResult):
        self.message_repository.save_message_result(ppurio_message_result)

        if self.is_lms_success(ppurio_message_result):
            print("lms success")
            # DB 성공 상태 업데이트

    def is_lms_success(self, ppurio_message_result):
        return ppurio_message_result.MEDIA == "LMS" and ppurio_message_result.RESULT == "6600"
