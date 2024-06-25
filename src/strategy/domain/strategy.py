from datetime import datetime

from pydantic import BaseModel

from src.audiences.enums.audience_type import AudienceType
from src.strategy.domain.strategy_theme import (
    StrategyTheme,
    StrategyThemeAudienceMapping,
    StrategyThemeOfferMapping,
)
from src.strategy.enums.strategy_status import StrategyStatus
from src.strategy.enums.target_strategy import TargetStrategy
from src.strategy.infra.entity.strategy_entity import StrategyEntity
from src.strategy.routes.dto.request.strategy_create import StrategyCreate


class Strategy(BaseModel):
    strategy_id: str | None = None
    strategy_name: str
    strategy_tags: list | None = None
    strategy_status_code: str
    strategy_status_name: str
    audience_type_code: str
    audience_type_name: str
    target_strategy_code: str
    target_strategy_name: str
    owned_by_dept: str | None = None
    created_at: datetime | None = None
    created_by: str | None = None
    updated_at: datetime | None = None
    updated_by: str | None = None
    strategy_themes: list[StrategyTheme] = []

    @staticmethod
    def from_entity(entity: StrategyEntity) -> "Strategy":
        strategy_themes = [
            StrategyTheme(
                strategy_theme_id=theme.strategy_theme_id,
                strategy_theme_name=theme.strategy_theme_name,
                strategy_id=theme.strategy_id,
                recsys_model_id=theme.recsys_model_id,
                contents_tags=theme.contents_tags,
                created_at=theme.created_at,
                created_by=theme.created_by,
                updated_at=theme.updated_at,
                updated_by=theme.updated_by,
                strategy_theme_audience_mapping=[
                    StrategyThemeAudienceMapping.model_validate(audience)
                    for audience in theme.strategy_theme_audience_mapping
                ],
                strategy_theme_offer_mapping=[
                    StrategyThemeOfferMapping.model_validate(offer)
                    for offer in theme.strategy_theme_offer_mapping
                ],
            )
            for theme in entity.strategy_themes
        ]

        # Convert StrategyEntity to StrategyModel
        strategy_model = Strategy(
            strategy_id=entity.strategy_id,
            strategy_name=entity.strategy_name,
            strategy_tags=entity.strategy_tags,
            strategy_status_code=entity.strategy_status_code,
            strategy_status_name=entity.strategy_status_name,
            audience_type_code=entity.audience_type_code,
            audience_type_name=entity.audience_type_name,
            target_strategy_code=entity.target_strategy_code,
            target_strategy_name=entity.target_strategy_name,
            owned_by_dept=entity.owned_by_dept,
            created_at=entity.created_at,
            created_by=entity.created_by,
            updated_at=entity.updated_at,
            updated_by=entity.updated_by,
            strategy_themes=strategy_themes,
        )

        return strategy_model

    @staticmethod
    def from_create(strategy_create: StrategyCreate) -> "Strategy":
        return Strategy(
            strategy_name=strategy_create.strategy_name,
            strategy_tags=strategy_create.strategy_tags,
            strategy_status_code=StrategyStatus.inactive.value,
            strategy_status_name=StrategyStatus.inactive.description,
            audience_type_code=strategy_create.audience_type_code,
            audience_type_name=AudienceType(
                strategy_create.audience_type_code
            ).description,
            target_strategy_code=strategy_create.target_strategy_code.value,
            target_strategy_name=TargetStrategy(
                strategy_create.target_strategy_code
            ).description,
        )
