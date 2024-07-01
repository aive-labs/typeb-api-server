from abc import ABC, abstractmethod


class UpdateStrategyUseCase(ABC):

    @abstractmethod
    def exec(self, strategy_id: str):
        pass
