from datetime import datetime

from pydantic import BaseModel

from src.strategy.routes.dto.common import ThemeDetail


class CampaignThemeSelectV2(BaseModel):
    campaign_theme_id: int
    campaign_theme_name: str
    recsys_model_id: int
    theme_audience_set: ThemeDetail


class StrategyWithCampaignThemeResponse(BaseModel):
    strategy_name: str
    strategy_tags: list | None = None
    strategy_metric_code: str
    strategy_metric_name: str
    strategy_status_code: str
    strategy_status_name: str
    audience_type_code: str
    audience_type_name: str
    target_group_code: str
    target_group_name: str
    campaign_themes: list[CampaignThemeSelectV2]
    created_at: datetime
    updated_at: datetime
