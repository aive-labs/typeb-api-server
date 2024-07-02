from abc import ABC, abstractmethod

from sqlalchemy.orm import Session

from src.strategy.domain.strategy import Strategy
from src.strategy.domain.strategy_theme import StrategyTheme
from src.strategy.routes.dto.response.strategy_with_campaign_theme_response import (
    StrategyThemeSelectV2,
)
from src.users.domain.user import User


class BaseStrategyRepository(ABC):
    @abstractmethod
    def get_all_strategies(
        self, start_date, end_date, user: User, db: Session
    ) -> list[Strategy]:
        pass

    @abstractmethod
    def get_strategy_detail(
        self, strategy_id: str, db: Session
    ) -> tuple[Strategy, list[StrategyThemeSelectV2]]:
        pass

    @abstractmethod
    def create_strategy(
        self,
        strategy: Strategy,
        campaign_themes: list[StrategyTheme],
        user: User,
    ):
        pass

    @abstractmethod
    def is_strategy_name_exists(self, name: str, db: Session) -> int:
        pass

    @abstractmethod
    def find_by_strategy_id(self, strategy_id: str) -> Strategy:
        pass

    @abstractmethod
    def delete(self, strategy_id: str, db: Session):
        pass

    @abstractmethod
    def update(
        self,
        strategy: Strategy,
        campaign_themes: list[StrategyTheme],
        user: User,
        db: Session,
    ):
        pass
