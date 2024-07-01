from abc import ABC, abstractmethod

from src.strategy.routes.dto.request.strategy_create import StrategyCreate


class UpdateStrategyUseCase(ABC):

    @abstractmethod
    def exec(self, strategy_id: str, strategy_update: StrategyCreate):
        pass
