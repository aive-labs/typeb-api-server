from abc import ABC, abstractmethod

from sqlalchemy.orm import Session

from src.strategy.routes.dto.response.strategy_response import StrategyResponse
from src.strategy.routes.dto.response.strategy_with_campaign_theme_response import (
    StrategyWithStrategyThemeResponse,
)
from src.user.domain.user import User


class GetStrategyUseCase(ABC):
    @abstractmethod
    def get_strategies(
        self, start_date: str, end_date: str, user: User, db: Session
    ) -> list[StrategyResponse]:
        pass

    @abstractmethod
    def get_strategy_detail(
        self, strategy_id: str, db: Session
    ) -> StrategyWithStrategyThemeResponse:
        pass
