from fastapi import Depends

from src.auth.utils.get_current_user import get_current_user
from src.users.domain.gnb_permission import ContentsManager, GNBPermissions
from src.users.domain.resource_permission import ResourcePermission
from src.users.domain.user_role import UserPermissions, UserRole


def create_user_role(role: str) -> UserRole:
    role_mapping = {
        "admin": ("admin", "관리자"),
        "operator": ("operator", "운영자"),
        "user": ("user", "본사 사용자"),
        "branch_user": ("branch_user", "매장 사용자"),
        # User role 추가시 role_mapping에 추가
    }

    if role not in role_mapping:
        raise ValueError("Invalid role provided")

    role_id, role_name = role_mapping[role]
    return UserRole(role_id=role_id, role_name=role_name)


def create_resource_permission(user_role: UserRole) -> ResourcePermission:
    if user_role.role_id in ["admin", "operator"]:
        resource_permission_id, resource_permission_name = "all_access", "전체"
    elif user_role.role_id == "user":
        resource_permission_id, resource_permission_name = "team_access", "팀 리소스"
    else:
        resource_permission_id, resource_permission_name = (
            "branch_access",
            "지점 리소스",
        )
    return ResourcePermission(
        resource_permission_id=resource_permission_id,
        resource_permission_name=resource_permission_name,
    )


def generate_gnb_permissions(user_role: UserRole, user) -> GNBPermissions:
    """사용자의 GNB 및 메뉴별 권한을 설정하는 함수
    To-do: DB에서 팀, 유저별 권한을 조회하여 설정하는 로직 추가
    """
    gnb_permissions = GNBPermissions()
    if user_role.role_id == "admin":
        gnb_permissions.strategy_manager = ["create", "read", "update", "delete"]
        gnb_permissions.contents_manager = ContentsManager()
        gnb_permissions.contents_manager.contents_library = [
            "create",
            "read",
            "update",
            "delete",
        ]
        gnb_permissions.settings.templates = ["create", "read", "update", "delete"]
        gnb_permissions.settings.offer = ["read", "update"]
        gnb_permissions.settings.admin = ["create", "read", "update", "delete"]
        gnb_permissions.dashboard.campaigns = ["read"]
        gnb_permissions.dashboard.trend_analysis = ["read"]
        gnb_permissions.dashboard.audience_analysis = ["read"]
    elif user_role.role_id == "operator":
        gnb_permissions.strategy_manager = ["create", "read", "update", "delete"]
        gnb_permissions.contents_manager = ContentsManager()
        gnb_permissions.settings.offer = ["read", "update"]
        gnb_permissions.dashboard.campaigns = ["read"]
        gnb_permissions.dashboard.trend_analysis = ["read"]
        gnb_permissions.dashboard.audience_analysis = ["read"]
    elif user_role.role_id == "user":
        # 마케팅커뮤니케이션팀 - 콘텐츠 매니저 생성/수정/삭제 권한 부여
        if user.department_id == "50B500":
            gnb_permissions.contents_manager = ContentsManager()
        gnb_permissions.settings.offer = ["read"]
        gnb_permissions.dashboard.campaigns = ["read"]
        gnb_permissions.dashboard.trend_analysis = ["read"]
        gnb_permissions.dashboard.audience_analysis = ["read"]
    return gnb_permissions


def get_user_permissions(user_role: UserRole, user) -> UserPermissions:
    """사용자의 GNB 및 메뉴별 권한, 리소스 접근 권한을 설정하는 함수
    To-do: DB에서 팀, 유저별 권한을 조회하여 설정하는 로직 추가
    """
    user_permissions = UserPermissions(
        gnb_permissions=generate_gnb_permissions(user_role, user),
        resource_permission=create_resource_permission(user_role),
        user_role=user_role,
    )
    # To-do: '관리자 > 오퍼권한' 및 '콘텐츠 등록권한'을 팀, 유저단위로 권한을 부여하는 케이스에 대해서 추가

    return user_permissions


class PermissionChecker:
    def __init__(self, required_permissions: list[str]) -> None:
        """API를 호출하는 유저가 권한이 있는지 체크하는 디펜던시

        Args:
            required_permissions (list[str]): API 호출시 필요한 권한이며, 리스트 타입으로 입력
        """
        # requeired_permissions: API 호출시 필요한 권한 (하나 이상의 권한이 필요한 경우, 리스트로 입력)
        self.required_permissions = required_permissions

    def __call__(self, user=Depends(get_current_user)):
        """Checks if the user has the required permissions for API access.

        Args:
            user: The user object obtained from the `verify_user` dependency.

        Raises:
            HTTPException: 퍼미션 권한이 없는 케이스가 Null 이거나 Empty list 인 경우, 403 에러를 발생시킵니다.
            HTTPException: 필요한 권한이 없는 경우, 필요한 권한을 알려주고 403 에러를 발생시킵니다.
        """
        print(user.role_id)
        create_user_role(user.role_id)
        # permissions = get_user_permissions(user_role, user).model_dump()
        # for r_perm in self.required_permissions:
        #     parts = r_perm.split(":")
        #     current_json = permissions
        #
        #     for part in parts:
        #         if isinstance(current_json, dict):
        #             current_json = current_json.get(part)
        #         else:
        #             break
        #
        #     if current_json is None or len(current_json) == 0:
        #         raise HTTPException(
        #             status_code=403,
        #             detail={
        #                 "code": "access/denied",
        #                 "message": "접근 권한이 존재하지 않습니다.",
        #             },
        #         )
        #
        #     if parts[-1] in current_json:
        #         continue
        #     else:
        #         raise HTTPException(
        #             status_code=403,
        #             detail={
        #                 "code": "access/invalid",
        #                 "message": f"권한이 부족합니다. ({r_perm}) 권한이 필요합니다.",
        #             },
        #         )
        return user


def get_permission_checker(required_permissions):
    return PermissionChecker(required_permissions)
