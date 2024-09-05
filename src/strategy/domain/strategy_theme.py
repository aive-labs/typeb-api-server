from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class StrategyThemeAudienceMapping(BaseModel):
    strategy_theme_id: int | None = None
    audience_id: str
    created_at: datetime | None = None
    created_by: str | None = None
    updated_at: datetime | None = None
    updated_by: str | None = None

    class Config:
        from_attributes = True


class StrategyThemeOfferMapping(BaseModel):
    strategy_theme_id: int | None = None
    coupon_no: str
    created_at: datetime | None = None
    created_by: str | None = None
    updated_at: datetime | None = None
    updated_by: str | None = None

    class Config:
        from_attributes = True


class StrategyTheme(BaseModel):
    strategy_theme_id: int | None = None
    strategy_theme_name: str
    strategy_id: Optional[str] | None = None
    recsys_model_id: int
    contents_tags: list[str] | None = None
    created_at: datetime | None = None
    created_by: str | None = None
    updated_at: datetime | None = None
    updated_by: str | None = None
    strategy_theme_audience_mapping: list[StrategyThemeAudienceMapping] = []
    strategy_theme_offer_mapping: list[StrategyThemeOfferMapping] = []
