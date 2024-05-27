from pydantic import BaseModel

from src.audiences.domain.audience import Audience


class CodeItems(BaseModel):
    id: str | int | None = None
    name: str | None = None


class AudienceFilter(BaseModel):
    rep_list: list[CodeItems] | None = None


class AudienceResponse(BaseModel):
    audiences: list[Audience]
    filters: AudienceFilter

    class Config:
        from_attributes = True
