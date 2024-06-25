from abc import ABC, abstractmethod

from src.strategy.routes.dto.request.strategy_create import StrategyCreate
from src.users.domain.user import User


class CreateStrategyUseCase(ABC):
    @abstractmethod
    def create_strategy_object(self, strategy_create: StrategyCreate, user: User):
        pass
