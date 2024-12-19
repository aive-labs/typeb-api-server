from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class ContentsMenu(BaseModel):
    id: int
    menu_type: str
    name: str
    code: str
    style_yn: str
    subject_with: Optional[str]
    created_by: str
    created_at: Optional[datetime]
    updated_by: str
    updated_at: Optional[datetime]
