from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field
from users.domain.user import User
from utils.date_utils import localtime_converter


class UserResponse(BaseModel):
    user_id: int
    username: str
    email: Optional[str] = None
    photo_uri: Optional[str] = None
    # permissions: dict
    department_id: str
    department_name: Optional[str] = None
    parent_dept_cd: Optional[str] = None
    language: str
    test_callback_number: str
    last_login: Optional[datetime] = None
    # created_at: datetime = Field(default_factory=localtime_converter)
    # updated_at: datetime = Field(default_factory=localtime_converter)
