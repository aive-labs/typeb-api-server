from src.strategy.domain.campaign_theme import StrategyTheme
from src.strategy.domain.strategy import Strategy
from src.strategy.infra.strategy_sqlalchemy_repository import StrategySqlAlchemy
from src.strategy.routes.dto.common import ThemeDetail
from src.strategy.routes.dto.response.strategy_with_campaign_theme_response import (
    CampaignThemeSelectV2,
)
from src.strategy.service.port.base_strategy_repository import BaseStrategyRepository
from src.users.domain.user import User


class StrategyRepository(BaseStrategyRepository):
    def __init__(self, strategy_sqlalchemy: StrategySqlAlchemy):
        self.strategy_sqlalchemy_repository = strategy_sqlalchemy

    def get_all_strategies(self, start_date, end_date, user: User) -> list[Strategy]:
        return self.strategy_sqlalchemy_repository.get_all_strategies(
            start_date, end_date, user
        )

    def get_strategy_detail(
        self, strategy_id: str
    ) -> tuple[Strategy, list[CampaignThemeSelectV2]]:
        strategy_entity = self.strategy_sqlalchemy_repository.get_strategy_detail(
            strategy_id=strategy_id
        )

        campaign_theme_obj = [
            CampaignThemeSelectV2(
                campaign_theme_id=theme.strategy_theme_id,
                campaign_theme_name=theme.strategy_theme_name,
                recsys_model_id=theme.recsys_model_id,
                theme_audience_set=ThemeDetail(
                    audience_ids=[
                        audience.audience_id
                        for audience in theme.theme_audience_mapping
                    ],
                    offer_ids=[offer.offer_id for offer in theme.theme_offer_mapping],
                    contents_tags=theme.contents_tags,
                ),
            )
            for theme in strategy_entity.campaign_themes
        ]

        return Strategy.from_entity(strategy_entity), campaign_theme_obj

    def create_strategy(
        self, strategy: Strategy, campaign_themes: list[StrategyTheme], user: User
    ):
        self.strategy_sqlalchemy_repository.create_strategy(
            strategy, campaign_themes, user
        )

    def is_strategy_name_exists(self, name: str) -> int:
        return self.strategy_sqlalchemy_repository.is_strategy_name_exists(name)

    def find_by_strategy_id(self, strategy_id: str) -> Strategy:
        return self.strategy_sqlalchemy_repository.find_by_strategy_id(strategy_id)
