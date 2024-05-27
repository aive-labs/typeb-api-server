from datetime import datetime

from pydantic import BaseModel
from users.infra.entity.user_entity import UserEntity


class User(BaseModel):
    user_id: int | None = None
    username: str
    password: str | None = None
    email: str
    photo_uri: str | None = None
    role_id: str
    permissions: dict | None = None
    department_id: str | None = None
    department_name: str | None = None
    parent_dept_cd: str | None = None
    parent_dept_cd: str | None = None
    language: str
    test_callback_number: str | None = None
    last_login: datetime | None = None

    def to_entity(self) -> UserEntity:
        return UserEntity(
            username=self.username,
            email=self.email,
            password=self.password,
            role_id=self.role_id,
            photo_uri=self.photo_uri,
            department_id=self.department_id,
            language=self.language,
            test_callback_number=self.test_callback_number,
        )

    @staticmethod
    def from_entity(user_entity: UserEntity) -> "User":
        return User(
            user_id=user_entity.user_id,
            username=user_entity.username,
            email=user_entity.email,
            photo_uri=user_entity.photo_uri,
            role_id=user_entity.role_id,
            department_id=user_entity.department_id,
            department_name=user_entity.department_name,
            parent_dept_cd=user_entity.parent_dept_cd,
            language=user_entity.language,
            test_callback_number=user_entity.test_callback_number,
            last_login=user_entity.last_login,
        )
