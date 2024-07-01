from datetime import datetime

from pydantic import BaseModel

from src.strategy.routes.dto.common import ThemeDetail


class StrategyThemeSelectV2(BaseModel):
    strategy_theme_id: int | None = None
    strategy_theme_name: str
    recsys_model_id: int
    theme_audience_set: ThemeDetail | None = None


class StrategyWithStrategyThemeResponse(BaseModel):
    strategy_name: str
    strategy_tags: list[str] | None = None
    strategy_status_code: str
    strategy_status_name: str
    audience_type_code: str
    audience_type_name: str
    target_strategy_code: str
    target_strategy_name: str
    strategy_themes: list[StrategyThemeSelectV2]
    created_at: datetime
    updated_at: datetime
