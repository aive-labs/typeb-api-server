from pydantic import BaseModel

from src.audiences.domain.audience import Audience
from src.audiences.routes.dto.response.code_items import CodeItems


class AudienceFilter(BaseModel):
    rep_list: list[CodeItems] | None = None


class AudienceResponse(BaseModel):
    audiences: list[Audience]
    filters: AudienceFilter

    class Config:
        from_attributes = True
