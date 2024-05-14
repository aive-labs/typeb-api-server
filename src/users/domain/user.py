from datetime import datetime
from typing import Optional
from pydantic import BaseModel

from users.infra.entity.user_entity import UserEntity


class User(BaseModel):
    user_id: Optional[int] = None
    username: str
    email: Optional[str] = None
    photo_uri: Optional[str] = None
    role_id: str
    permissions: Optional[dict] = None
    department_id: Optional[str] = None
    department_name: Optional[str] = None
    parent_dept_cd: Optional[str] = None
    language: str
    test_callback_number: str
    last_login: Optional[datetime] = None

    def to_entity(self) -> UserEntity:
        return UserEntity(
            username=self.username,
            email=self.email,
            role_id=self.role_id,
            photo_uri=self.photo_uri,
            department_id=self.department_id,
            language=self.language,
            test_callback_number=self.test_callback_number,
        )

    @staticmethod
    def from_entity(user_entity: UserEntity):
        return User(
            user_id=user_entity.user_id,
            username=user_entity.username,
            email=user_entity.email,
            role_id=user_entity.role_id,
            photo_uri=user_entity.photo_uri,
            department_id=user_entity.department_id,
            department_name=user_entity.department_name,
            parent_dept_cd=user_entity.parent_dept_cd,
            test_callback_number=user_entity.test_callback_number,
            language=user_entity.language,
            last_login=user_entity.last_login,
        )
