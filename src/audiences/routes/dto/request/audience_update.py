## 오디언스 수정 스키마
from datetime import datetime

from pydantic import BaseModel

from src.audiences.routes.dto.request.audience_create import FilterObj


class AudienceUpdate(BaseModel):
    audience_name: str
    create_type_code: str
    filters: list[FilterObj] | None = None
    exclusions: list[FilterObj] | None = None
    upload: dict | None = None
    updated_at: datetime = datetime.now()
