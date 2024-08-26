from fastapi import Depends

from src.auth.utils.get_current_user import get_current_user
from src.core.exceptions.exceptions import AuthorizationException
from src.users.domain.gnb_permission import ContentsManager, GNBPermissions
from src.users.domain.resource_permission import ResourcePermission
from src.users.domain.user_role import UserPermissions, UserRole
from src.users.utils.user_role_mapping import get_user_role_from_mapping


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
        get_user_role_from_mapping(user.role_id)

        if "subscription" in self.required_permissions and user.subscription is None:
            raise AuthorizationException(
                detail={"message": "해당 기능은 플랜 결제 후 사용 가능합니다."}
            )

        return user


def get_permission_checker(required_permissions: list[str]):
    return PermissionChecker(required_permissions)
