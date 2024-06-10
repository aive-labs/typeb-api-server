from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

from src.utils.date_utils import localtime_converter


class UserModify(BaseModel):
    user_id: int
    username: Optional[str] = None
    language: Optional[str] = None
    test_callback_number: Optional[str] = None
    updated_at: datetime = Field(default_factory=localtime_converter)
