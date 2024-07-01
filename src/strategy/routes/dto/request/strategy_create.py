from datetime import datetime

from pydantic import BaseModel, Field

from src.common.utils.date_utils import localtime_converter
from src.strategy.enums.target_strategy import TargetStrategy
from src.strategy.routes.dto.common import StrategyThemeModel


class StrategyCreate(BaseModel):
    strategy_name: str
    strategy_tags: list | None = None
    audience_type_code: str
    target_strategy: TargetStrategy
    strategy_themes: list[StrategyThemeModel]
    created_at: datetime = Field(default_factory=localtime_converter)
    updated_at: datetime = Field(default_factory=localtime_converter)
