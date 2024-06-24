from pydantic import BaseModel


class ThemeAudience(BaseModel):
    audience_id: str
    campaign_theme_id: int | None = None


class ThemeOffer(BaseModel):
    offer_id: str
    campaign_theme_id: int | None = None


class StrategyTheme(BaseModel):
    strategy_theme_id: int | None = None
    strategy_theme_name: str
    recsys_model_id: int
    contents_tags: list[str]
    theme_audience: list[ThemeAudience] = []
    theme_offer: list[ThemeOffer] = []
