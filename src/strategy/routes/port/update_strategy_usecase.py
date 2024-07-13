from abc import ABC, abstractmethod

from sqlalchemy.orm import Session

from src.core.transactional import transactional
from src.strategy.routes.dto.request.strategy_create import StrategyCreate
from src.users.domain.user import User


class UpdateStrategyUseCase(ABC):

    @transactional
    @abstractmethod
    def exec(self, strategy_id: str, strategy_update: StrategyCreate, user: User, db: Session):
        pass
