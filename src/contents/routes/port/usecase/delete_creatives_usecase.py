from abc import ABC, abstractmethod

from sqlalchemy.orm import Session

from src.core.transactional import transactional


class DeleteCreativesUseCase(ABC):

    @transactional
    @abstractmethod
    def exec(self, creative_id: int, db: Session) -> None:
        pass
