from abc import ABC, abstractmethod

from sqlalchemy.orm import Session

from src.message_template.domain.message_template import MessageTemplate


class BaseMessageTemplateRepository(ABC):

    @abstractmethod
    def save_message_template(self, model: MessageTemplate, db: Session) -> MessageTemplate:
        pass

    @abstractmethod
    def get_all_templates(self, db: Session, media: str | None = None) -> list[MessageTemplate]:
        pass

    @abstractmethod
    def get_template_detail(self, template_id: str, db: Session) -> MessageTemplate:
        pass

    @abstractmethod
    def update(self, template_id: str, model: MessageTemplate, db: Session):
        pass

    @abstractmethod
    def delete(self, template_id: str, db: Session):
        pass
