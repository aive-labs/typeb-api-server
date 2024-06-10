from typing import Optional

from pydantic import BaseModel

from src.users.domain.user_role import UserPermissions


class UserProfileResponse(BaseModel):
    user_id: int
    username: str
    email: Optional[str] = None
    photo_uri: Optional[str] = None
    permissions: UserPermissions
    department_id: str
    department_name: Optional[str] = None
    parent_dept_cd: Optional[str] = None
    language: str
    test_callback_number: str

    @staticmethod
    def from_user(user, permissions: UserPermissions):
        return UserProfileResponse(
            user_id=user.user_id,
            username=user.username,
            email=user.email,
            photo_uri=user.photo_uri,
            permissions=permissions,
            department_id=user.department_id,
            department_name=user.department_name,
            parent_dept_cd=user.parent_dept_cd,
            language=user.language,
            test_callback_number=(
                user.test_callback_number if user.sys_id == "WP" else "1666-3096"
            ),
        )
