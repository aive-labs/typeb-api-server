from pydantic import BaseModel


class ThemeDetail(BaseModel):
    audience_ids: list[str]
    coupon_no_list: list[str]
    contents_tags: list[str] | None = None


class StrategyThemeModel(BaseModel):
    strategy_theme_id: int | None = None
    strategy_theme_name: str
    recsys_model_id: int
    theme_audience_set: ThemeDetail
