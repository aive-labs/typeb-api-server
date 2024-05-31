from abc import ABC, abstractmethod

from src.strategy.routes.dto.request.strategy_create import StrategyCreate
from src.users.domain.user import User


class CreateStrategyUsecase(ABC):

    @abstractmethod
    def create_strategy_object(
        self, create_strategy_service: StrategyCreate, user: User
    ):
        pass
