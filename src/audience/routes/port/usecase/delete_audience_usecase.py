from abc import ABC, abstractmethod

from sqlalchemy.orm import Session

from src.core.transactional import transactional


class DeleteAudienceUseCase(ABC):
    @transactional
    @abstractmethod
    def exec(self, audience_id: str, db: Session):
        pass
