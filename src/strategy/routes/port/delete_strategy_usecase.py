from abc import ABC, abstractmethod

from src.core.transactional import transactional


class DeleteStrategyUseCase(ABC):

    @transactional
    @abstractmethod
    def exec(self, strategy_id: str):
        pass
