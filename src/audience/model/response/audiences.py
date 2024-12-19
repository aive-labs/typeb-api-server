from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class FilterItem(BaseModel):
    id: str
    name: str


class AudienceFilter(BaseModel):
    rep_list: list[FilterItem] | None = None
    owned_by_dept_list: list[FilterItem] | None = None


class AudienceRes(BaseModel):
    audience_id: str
    audience_name: str
    audience_status_code: str
    audience_status_name: str
    is_exclude: bool
    user_exc_deletable: Optional[bool]
    update_cycle: str
    description: Optional[str]
    audience_count: int
    audience_unit_price: float
    rep_list: list[FilterItem] | None = None
    created_at: datetime
    updated_at: datetime
    owned_by_dept: str | None = None


class AudienceResponse(BaseModel):
    audiences: list[AudienceRes]
    filters: AudienceFilter | None = None

    class Config:
        from_attributes = True
