## 오디언스 수정 스키마
from datetime import datetime

from pydantic import BaseModel

from src.audiences.routes.dto.request.audience_create import FilterObj
from src.strategy.enums.target_strategy import TargetStrategy


class AudienceUpdate(BaseModel):
    audience_name: str
    create_type_code: str
    target_strategy: TargetStrategy
    filters: list[FilterObj] | None = None
    exclusions: list[FilterObj] | None = None
    upload: dict | None = None
    updated_at: datetime | None = None
