from abc import ABC, abstractmethod

from src.core.transactional import transactional
from src.strategy.routes.dto.request.strategy_create import StrategyCreate


class UpdateStrategyUseCase(ABC):

    @transactional
    @abstractmethod
    def exec(self, strategy_id: str, strategy_update: StrategyCreate):
        pass
