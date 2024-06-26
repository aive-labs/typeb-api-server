from src.message_template.infra.message_template_repository import (
    MessageTemplateRepository,
)
from src.message_template.routes.port.delete_message_template_usecase import (
    DeleteMessageTemplateUseCase,
)


class DeleteMessageTemplateService(DeleteMessageTemplateUseCase):

    def __init__(self, message_template_repository: MessageTemplateRepository):
        self.message_template_repository = message_template_repository

    def exec(self, template_id: str):
        self.message_template_repository.delete(template_id)
