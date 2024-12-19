from abc import ABC, abstractmethod

from sqlalchemy.orm import Session

from src.core.transactional import transactional
from src.message_template.routes.dto.request.message_template_update import (
    TemplateUpdate,
)
from src.user.domain.user import User


class UpdateMessageTemplateUseCase(ABC):

    @transactional
    @abstractmethod
    def exec(self, template_id: str, template_update: TemplateUpdate, user: User, db: Session):
        pass
