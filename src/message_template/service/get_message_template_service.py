from sqlalchemy.orm import Session

from src.message_template.domain.message_template import MessageTemplate
from src.message_template.routes.port.get_message_template_usecase import (
    GetMessageTemplateUseCase,
)
from src.message_template.service.port.base_message_template_repository import (
    BaseMessageTemplateRepository,
)


class GetMessageTemplateService(GetMessageTemplateUseCase):

    def __init__(self, message_template_repository: BaseMessageTemplateRepository):
        self.message_template_repository = message_template_repository

    def get_all_templates(self, db: Session, media: str | None = None) -> list[MessageTemplate]:
        return self.message_template_repository.get_all_templates(db=db, media=media)

    def get_template_detail(self, template_id: str, db: Session) -> MessageTemplate:
        return self.message_template_repository.get_template_detail(template_id, db)
