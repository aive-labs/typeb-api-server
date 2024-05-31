from src.strategy.domain.campaign_theme import CampaignTheme
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
        self.strategy_sqlalchemy_respository = strategy_sqlalchemy

    def get_all_strategies(self, start_date, end_date, user: User) -> list[Strategy]:
        strategy_entities = self.strategy_sqlalchemy_respository.get_all_strategies(
            start_date, end_date, user
        )

        return [Strategy.from_entity(entity) for entity in strategy_entities]

    def get_strategy_detail(
        self, strategy_id: str
    ) -> tuple[Strategy, list[CampaignThemeSelectV2]]:
        strategy_entity = self.strategy_sqlalchemy_respository.get_strategy_detail(
            strategy_id=strategy_id
        )

        campaign_theme_obj = [
            CampaignThemeSelectV2(
                campaign_theme_id=theme.campaign_theme_id,
                campaign_theme_name=theme.campaign_theme_name,
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
        self, strategy: Strategy, campaign_themes: list[CampaignTheme], user: User
    ):

        self.strategy_sqlalchemy_respository.create_strategy(
            strategy, campaign_themes, user
        )

    def is_strategy_name_exists(self, name: str) -> int:
        return self.strategy_sqlalchemy_respository.is_strategy_name_exists(name)
