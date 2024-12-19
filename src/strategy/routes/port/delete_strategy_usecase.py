from abc import ABC, abstractmethod

from sqlalchemy.orm import Session

from src.main.transactional import transactional


class DeleteStrategyUseCase(ABC):

    @transactional
    @abstractmethod
    def exec(self, strategy_id: str, db: Session):
        pass
