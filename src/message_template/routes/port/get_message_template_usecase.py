from abc import ABC, abstractmethod

from src.message_template.domain.message_template import MessageTemplate


class GetMessageTemplateUseCase(ABC):

    @abstractmethod
    def get_all_templates(self, media: str | None = None) -> list[MessageTemplate]:
        pass

    @abstractmethod
    def get_template_detail(self, template_id: str) -> MessageTemplate:
        pass
