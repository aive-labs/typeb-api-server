from typing import Optional

from pydantic import BaseModel

from src.auth.infra.dto.external_integration import ExternalIntegration
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
    mall_id: Optional[str] = None
    onboarding_status: str
    cafe24: Optional[ExternalIntegration] | None = None

    @staticmethod
    def from_user(
        user,
        permissions: UserPermissions,
        cafe24_integration: Optional[ExternalIntegration] | None,
        onboarding_status: str,
    ):
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
                user.test_callback_number if user.sys_id == "WP" else "02-2088-5502"
            ),
            mall_id=None if cafe24_integration is None else cafe24_integration.mall_id,
            onboarding_status=onboarding_status,
            cafe24=cafe24_integration,
        )
