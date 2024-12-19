from abc import ABC, abstractmethod

from sqlalchemy.orm import Session

from src.strategy.routes.dto.request.strategy_create import StrategyCreate
from src.user.domain.user import User


class CreateStrategyUseCase(ABC):
    @abstractmethod
    def create_strategy_object(self, strategy_create: StrategyCreate, user: User, db: Session):
        pass
