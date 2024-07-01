from abc import ABC, abstractmethod


class DeleteStrategyUseCase(ABC):

    @abstractmethod
    def exec(self, strategy_id: str):
        pass
