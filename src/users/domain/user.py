from datetime import datetime

from passlib.context import CryptContext
from pydantic import BaseModel

from src.payment.routes.dto.response.my_subscription import MySubscription
from src.users.infra.entity.user_entity import UserEntity
from src.users.infra.entity.user_password import UserPasswordEntity

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class User(BaseModel):
    user_id: int | None = None
    username: str
    password: str | None = None
    email: str
    photo_uri: str | None = None
    role_id: str
    sys_id: str | None = None
    erp_id: str | None = None
    permissions: dict | None = None
    department_id: str | None = None
    department_name: str | None = None
    brand_name_ko: str | None = None
    brand_name_en: str | None = None
    parent_dept_cd: str | None = None
    language: str
    cell_phone_number: str | None = None
    test_callback_number: str | None = None
    last_login: datetime | None = None
    mall_id: str | None = None
    subscription: MySubscription | None = None
    is_aivelabs_admin: bool | None = None

    def to_entity(self) -> UserEntity:
        return UserEntity(
            username=self.username,
            email=self.email,
            login_id=self.email,
            role_id=self.role_id,
            sys_id=self.sys_id,
            erp_id=self.erp_id,
            photo_uri=self.photo_uri,
            department_id=self.department_id,
            brand_name_ko=self.brand_name_ko,
            brand_name_en=self.brand_name_en,
            department_name=self.department_id,
            department_abb_name=self.department_id,
            language=self.language,
            cell_phone_number=self.cell_phone_number,
            test_callback_number=self.test_callback_number,
            is_aivelabs_admin=False,
        )

    def to_password_entity(self) -> UserPasswordEntity:
        if not self.password:
            raise ValueError("Password is required")

        hashed_password = pwd_context.hash(self.password)
        return UserPasswordEntity(
            login_id=self.email,
            login_pw=hashed_password,
            email=self.email,
        )

    @staticmethod
    def from_entity(user_entity: UserEntity) -> "User":
        return User(
            user_id=user_entity.user_id,
            username=user_entity.username,
            email=user_entity.email,
            photo_uri=user_entity.photo_uri,
            role_id=user_entity.role_id,
            sys_id=user_entity.erp_id,
            erp_id=user_entity.sys_id,
            department_id=user_entity.department_id,
            department_name=user_entity.department_name,
            brand_name_ko=user_entity.brand_name_ko,
            brand_name_en=user_entity.brand_name_en,
            parent_dept_cd=user_entity.parent_dept_cd,
            language=user_entity.language,
            test_callback_number=user_entity.test_callback_number,
            last_login=user_entity.last_login,
        )

    def is_admin(self):
        return self.role_id == "admin"
