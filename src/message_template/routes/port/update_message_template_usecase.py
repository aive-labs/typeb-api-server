from abc import ABC, abstractmethod

from src.message_template.routes.dto.request.message_template_update import (
    TemplateUpdate,
)
from src.users.domain.user import User


class UpdateMessageTemplateUseCase(ABC):

    @abstractmethod
    def exec(self, template_id: str, template_update: TemplateUpdate, user: User):
        pass
