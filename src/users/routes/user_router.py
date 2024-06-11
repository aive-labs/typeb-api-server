import logging

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordRequestForm

from src.auth.service.auth_service import AuthService
from src.auth.service.token_service import TokenService
from src.auth.utils.permission_checker import get_permission_checker
from src.core.container import Container
from src.users.domain.gnb_permission import GNBPermissions
from src.users.domain.resource_permission import ResourcePermission
from src.users.domain.user_role import UserPermissions
from src.users.routes.dto.request.user_create import UserCreate
from src.users.routes.dto.request.user_modify import UserModify
from src.users.routes.dto.response.user_profile_response import UserProfileResponse
from src.users.routes.dto.response.user_response import UserResponse
from src.users.routes.port.base_user_service import BaseUserService
from src.users.utils.user_role_mapping import get_user_role_from_mapping

logger = logging.getLogger(__name__)

user_router = APIRouter(
    tags=["Users"],
)


@user_router.post("/signup")
@inject  # UserService 주입
def sign_up(
    user_create: UserCreate,
    user_service: BaseUserService = Depends(dependency=Provide[Container.user_service]),
) -> UserResponse:
    logger.debug(f"user_service: {user_service}")
    saved_user = user_service.register_user(user_create)
    return saved_user


@user_router.get("/me")
@inject
def get_me(user=Depends(get_permission_checker(required_permissions=[]))):
    permissions = UserPermissions(
        gnb_permissions=GNBPermissions.with_admin(),
        resource_permission=ResourcePermission(
            resource_permission_id="all_access", resource_permission_name="전체"
        ),
        user_role=get_user_role_from_mapping(user.role_id),
    )

    return UserProfileResponse.from_user(user, permissions)


@user_router.post("/signin")
@inject
def sign_in(
    form_data: OAuth2PasswordRequestForm = Depends(),
    auth_service: AuthService = Depends(dependency=Provide[Container.auth_service]),
):
    login_id = form_data.username
    password = form_data.password

    token_response = auth_service.login(login_id, password)

    response = JSONResponse(content=token_response.model_dump())
    response.set_cookie(
        key="access_token",
        value=token_response.access_token,
        httponly=True,
        # secure=True,
        samesite="Lax",  # pyright: ignore [reportArgumentType]
    )

    return response


@user_router.put("/me", status_code=status.HTTP_200_OK)
@inject
def update_user_profile(
    user_modify: UserModify,
    user=Depends(get_permission_checker(required_permissions=[])),
    user_service: BaseUserService = Depends(dependency=Provide[Container.user_service]),
):
    user_service.update_user(user_modify)


@user_router.post("/refresh")
@inject
def refresh_access_token(
    user=Depends(get_permission_checker(required_permissions=[])),
    token_service: TokenService = Depends(dependency=Provide[Container.user_service]),
):
    access_token, access_token_expires = token_service.create_refresh_token(
        subject=user.login_id,
        subject_userid=str(user.user_id),
    )

    response = JSONResponse(
        content={
            "access_token": access_token,
            "token_type": "Bearer",
            "access_token_expires_in": access_token_expires,
        }
    )
    response.set_cookie(
        key="access_token", value=access_token, httponly=True, secure=True
    )

    return response
