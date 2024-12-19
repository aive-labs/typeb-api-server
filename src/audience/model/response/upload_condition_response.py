from datetime import datetime

from pydantic import BaseModel


class UploadOptionResponse(BaseModel):
    result: str
    type: str
    upload_count: int
    checked_list: list[str]


class AudienceCreationOptionsResponse(BaseModel):
    audience_name: str
    create_type_code: str | None = None
    create_type_name: str | None = None
    target_strategy: str | None = None
    filters: list | None = None
    exclusions: list | None = None
    upload: UploadOptionResponse | None = None
    created_at: datetime
    updated_at: datetime
