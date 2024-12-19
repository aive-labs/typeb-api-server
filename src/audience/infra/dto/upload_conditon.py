from datetime import datetime

from pydantic import BaseModel


class UploadCondition(BaseModel):
    audience_name: str
    audience_id: str
    template_type: str
    upload_count: int
    checked_count: int
    checked_list: list[str]
    create_type_code: str | None = None
    create_type_name: str | None = None
    created_at: datetime
    updated_at: datetime
