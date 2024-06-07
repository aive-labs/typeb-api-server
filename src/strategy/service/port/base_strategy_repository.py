from abc import ABC, abstractmethod

from src.strategy.domain.campaign_theme import CampaignTheme
from src.strategy.domain.strategy import Strategy
from src.strategy.routes.dto.response.strategy_with_campaign_theme_response import (
    CampaignThemeSelectV2,
)
from src.users.domain.user import User


class BaseStrategyRepository(ABC):
    @abstractmethod
    def get_all_strategies(self, start_date, end_date, user: User) -> list[Strategy]:
        pass

    @abstractmethod
    def get_strategy_detail(
        self, strategy_id: str
    ) -> tuple[Strategy, list[CampaignThemeSelectV2]]:
        pass

    @abstractmethod
    def create_strategy(
        self,
        strategy: Strategy,
        campaign_themes: list[CampaignTheme],
        user: User,
    ):
        pass

    @abstractmethod
    def is_strategy_name_exists(self, name: str) -> int:
        pass

    @abstractmethod
    def find_by_strategy_id(self, strategy_id: str) -> Strategy:
        pass
