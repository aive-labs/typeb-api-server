
from pydantic import BaseModel


class ThemeDetail(BaseModel):
    audience_ids: list[str]
    offer_ids: list[str]
    contents_tags: list[str]


class CampaignThemeModel(BaseModel):
    campaign_theme_id: int | None = None
    campaign_theme_name: str
    recsys_model_id: int
    theme_audience_set: ThemeDetail
