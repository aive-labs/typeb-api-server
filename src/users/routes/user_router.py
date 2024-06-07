import logging

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends

from src.core.container import Container
from src.users.routes.dto.request.user_create_request import UserCreate
from src.users.routes.dto.response.user_response import UserResponse
from src.users.routes.port.base_user_service import BaseUserService

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
