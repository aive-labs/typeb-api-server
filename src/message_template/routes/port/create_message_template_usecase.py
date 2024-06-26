from abc import ABC, abstractmethod

from src.message_template.domain.message_template import MessageTemplate
from src.message_template.routes.dto.request.message_template_create import (
    TemplateCreate,
)
from src.users.domain.user import User


class CreateMessageTemplateUseCase(ABC):

    @abstractmethod
    def exec(self, template_create: TemplateCreate, user: User) -> MessageTemplate:
        pass