from sqlalchemy.orm import Session

from src.search.model.id_with_item_response import IdWithItem
from src.search.model.strategy_search_response import StrategySearchResponse
from src.strategy.domain.strategy import Strategy
from src.strategy.domain.strategy_theme import StrategyTheme
from src.strategy.infra.strategy_sqlalchemy_repository import StrategySqlAlchemy
from src.strategy.model.common import ThemeDetail
from src.strategy.model.response.strategy_with_campaign_theme_response import (
    StrategyThemeSelectV2,
)
from src.strategy.service.port.base_strategy_repository import BaseStrategyRepository
from src.user.domain.user import User


class StrategyRepository(BaseStrategyRepository):

    def __init__(self, strategy_sqlalchemy: StrategySqlAlchemy):
        self.strategy_sqlalchemy_repository = strategy_sqlalchemy

    def get_all_strategies(self, start_date, end_date, user: User, db: Session) -> list[Strategy]:
        return self.strategy_sqlalchemy_repository.get_all_strategies(
            start_date, end_date, user, db=db
        )

    def get_strategy_detail(
        self, strategy_id: str, db: Session
    ) -> tuple[Strategy, list[StrategyThemeSelectV2]]:
        strategy = self.strategy_sqlalchemy_repository.get_strategy_detail(
            strategy_id=strategy_id, db=db
        )

        strategy_themes = [
            StrategyThemeSelectV2(
                strategy_theme_id=theme.strategy_theme_id,
                strategy_theme_name=theme.strategy_theme_name,
                recsys_model_id=theme.recsys_model_id,
                theme_audience_set=ThemeDetail(
                    audience_ids=[
                        audience.audience_id for audience in theme.strategy_theme_audience_mapping
                    ],
                    coupon_no_list=[
                        offer.coupon_no for offer in theme.strategy_theme_offer_mapping
                    ],
                    contents_tags=theme.contents_tags,
                ),
            )
            for theme in strategy.strategy_themes
        ]

        return strategy, strategy_themes

    def create_strategy(
        self, strategy: Strategy, campaign_themes: list[StrategyTheme], user: User, db: Session
    ):
        self.strategy_sqlalchemy_repository.create_strategy(strategy, campaign_themes, user, db)

    def is_strategy_name_exists(self, name: str, db: Session) -> int:
        return self.strategy_sqlalchemy_repository.is_strategy_name_exists(name, db)

    def is_strategy_name_exists_for_update(self, strategy_id: str, name: str, db: Session) -> int:
        return self.strategy_sqlalchemy_repository.is_strategy_name_exists_for_update(
            strategy_id, name, db
        )

    def find_by_strategy_id(self, strategy_id: str) -> Strategy:
        return self.strategy_sqlalchemy_repository.find_by_strategy_id(strategy_id)

    def delete(self, strategy_id: str, db: Session):
        return self.strategy_sqlalchemy_repository.delete(strategy_id, db)

    def update_expired_strategy_status(self, strategy_id, db: Session):
        return self.strategy_sqlalchemy_repository.update_expired_strategy(strategy_id, db)

    def update(
        self,
        strategy: Strategy,
        campaign_themes: list[StrategyTheme],
        user: User,
        db: Session,
    ):
        return self.strategy_sqlalchemy_repository.update(strategy, campaign_themes, user, db)

    def search_keyword(
        self, campaign_type_code, search_keyword, db: Session
    ) -> list[StrategySearchResponse]:
        return self.strategy_sqlalchemy_repository.search_keyword(
            campaign_type_code, search_keyword, db
        )

    def search_strategy_themes_by_strategy_id(
        self, strategy_id: str, db: Session
    ) -> list[IdWithItem]:
        return self.strategy_sqlalchemy_repository.search_strategy_themes_by_strategy_id(
            strategy_id, db
        )

    def get_tags_search(self, strategy_theme_id, db: Session) -> tuple:
        return self.strategy_sqlalchemy_repository.get_tags(strategy_theme_id, db)

    def get_recsys_id_by_strategy_theme_by_id(self, strategy_theme_id, db: Session) -> int | None:
        return self.strategy_sqlalchemy_repository.get_recsys_id_by_strategy_theme_by_id(
            strategy_theme_id, db
        )
