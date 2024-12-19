from pydantic import BaseModel

from src.user.domain.gnb_permission import GNBPermissions
from src.user.domain.resource_permission import ResourcePermission


class UserRole(BaseModel):
    role_id: str
    role_name: str

    class Config:
        frozen = True


class UserPermissions(BaseModel):
    gnb_permissions: GNBPermissions
    resource_permission: ResourcePermission
    user_role: UserRole
