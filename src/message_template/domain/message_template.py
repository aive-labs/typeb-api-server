from datetime import datetime
from typing import Optional

from pydantic import BaseModel

from src.message_template.domain.message_template_button_detail import (
    MessageTemplateButtonDetail,
)


class MessageTemplate(BaseModel):
    template_id: int | None = None
    template_name: str
    media: str
    message_type: str
    message_title: str
    message_body: Optional[str]
    message_announcement: Optional[str]
    template_key: Optional[str]
    access_level: int
    owned_by_dept: str
    owned_by_dept_name: str
    created_at: datetime
    created_by: str
    updated_at: datetime
    updated_by: str
    button: list[MessageTemplateButtonDetail] = []

    class Config:
        from_attributes = True
