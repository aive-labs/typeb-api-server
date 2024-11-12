from pydantic import BaseModel

from src.users.domain.user import User


class UserCreate(BaseModel):
    username: str
    password: str
    email: str
    role_id: str
    photo_uri: str | None = None
    department_id: str
    brand_name_ko: str
    brand_name_en: str
    cell_phone_number: str | None = None
    test_callback_number: str | None = None
    language: str

    def to_user(self) -> "User":
        return User(
            username=self.username,
            password=self.password,
            email=self.email,
            role_id=self.role_id,
            photo_uri=self.photo_uri,
            department_id=self.department_id,
            brand_name_ko=self.brand_name_ko,
            brand_name_en=self.brand_name_en,
            cell_phone_number=self.cell_phone_number,
            test_callback_number=self.test_callback_number,
            language=self.language,
        )
