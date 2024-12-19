from datetime import datetime

from pydantic import BaseModel, Field

from src.common.utils.date_utils import localtime_converter
from src.strategy.model.common import StrategyThemeModel
from src.strategy.model.target_strategy import TargetStrategy


class StrategyCreate(BaseModel):
    strategy_name: str
    strategy_tags: list | None = None
    target_strategy: TargetStrategy
    strategy_themes: list[StrategyThemeModel]
    created_at: datetime = Field(default_factory=localtime_converter)
    updated_at: datetime = Field(default_factory=localtime_converter)
