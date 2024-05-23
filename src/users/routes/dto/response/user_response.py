from datetime import datetime

from pydantic import BaseModel


class UserResponse(BaseModel):
    user_id: int
    username: str
    email: str | None = None
    photo_uri: str | None = None
    # permissions: dict
    department_id: str
    department_name: str | None = None
    parent_dept_cd: str | None = None
    language: str
    test_callback_number: str
    last_login: datetime | None = None
    # created_at: datetime = Field(default_factory=localtime_converter)
    # updated_at: datetime = Field(default_factory=localtime_converter)
