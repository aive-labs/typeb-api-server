from abc import ABC, abstractmethod

from sqlalchemy.orm import Session

from src.main.transactional import transactional


class DeleteContentsUseCase(ABC):

    @transactional
    @abstractmethod
    def exec(self, contents_id: int, db: Session) -> None:
        pass
