from abc import ABC, abstractmethod

from sqlalchemy.orm import Session

from src.main.transactional import transactional


class DeleteMessageTemplateUseCase(ABC):

    @transactional
    @abstractmethod
    def exec(self, template_id: str, db: Session):
        pass
