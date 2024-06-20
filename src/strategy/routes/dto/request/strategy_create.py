from datetime import datetime

from pydantic import BaseModel, Field

from src.common.utils import localtime_converter
from src.strategy.routes.dto.common import CampaignThemeModel


class StrategyCreate(BaseModel):
    strategy_name: str
    strategy_tags: list | None = None
    strategy_metric_code: str
    audience_type_code: str
    target_group_code: str
    campaign_themes: list[CampaignThemeModel]
    created_at: datetime = Field(default_factory=localtime_converter)
    updated_at: datetime = Field(default_factory=localtime_converter)
