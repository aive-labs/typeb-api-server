from typing import Optional

from pydantic import BaseModel


class MessageTemplateButtonDetail(BaseModel):
    button_id: int | None = None
    template_id: int | None = None
    button_type: str
    button_name: str
    web_link: Optional[str]
    app_link: Optional[str]

    class Config:
        from_attributes = True
