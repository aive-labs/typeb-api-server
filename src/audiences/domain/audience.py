from datetime import datetime

from pydantic import BaseModel

from src.audiences.routes.dto.response.audiences import CodeItems


class Audience(BaseModel):
    audience_id: str
    audience_name: str
    audience_type_code: str
    audience_type_name: str
    audience_status_code: str
    audience_status_name: str
    is_exclude: bool
    user_exc_deletable: bool | None = None
    update_cycle: str
    description: str | None = None
    audience_count: int | None = None
    audience_unit_price: float | None = None
    rep_list: list[CodeItems] | None = None
    created_at: datetime = datetime.now()
    updated_at: datetime = datetime.now()
