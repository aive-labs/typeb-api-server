from abc import ABC, abstractmethod

from src.message_template.domain.message_template import MessageTemplate


class BaseMessageTemplateRepository(ABC):

    @abstractmethod
    def save_message_template(self, model: MessageTemplate) -> MessageTemplate:
        pass
