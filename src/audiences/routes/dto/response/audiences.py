from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class FilterItem(BaseModel):
    id: str
    name: str


class AudienceFilter(BaseModel):
    representative_items: list[FilterItem] | None = None
    audience_created_by: list[FilterItem] | None = None


class AudienceRes(BaseModel):
    audience_id: str
    audience_name: str
    audience_type_code: str
    audience_type_name: str
    audience_status_code: str
    audience_status_name: str
    is_exclude: bool
    user_exc_deletable: Optional[bool]
    update_cycle: str
    description: Optional[str]
    audience_count: int
    audience_unit_price: float
    rep_list: list[FilterItem]
    created_at: datetime
    updated_at: datetime
    owned_by_dept: str


class AudienceResponse(BaseModel):
    audiences: list[AudienceRes]
    filters: AudienceFilter

    class Config:
        from_attributes = True
