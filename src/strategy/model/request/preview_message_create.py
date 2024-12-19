from pydantic import BaseModel

from src.strategy.model.common import ThemeDetail


class PreviewMessageCreate(BaseModel):
    recsys_model_id: int
    theme_audience_set: ThemeDetail
