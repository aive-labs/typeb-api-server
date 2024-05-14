from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from dependency_injector.wiring import Provide, inject

import os

print(os.getcwd())

from core.container import Container
from users.routes.dto.request.user_create_request import UserCreate
from users.routes.dto.response.user_response import UserResponse
from users.routes.port.base_user_service import BaseUserService


user_router = APIRouter(
    tags=["Users"],
)


@user_router.post("/signup")
@inject  # UserService 주입
def sign_up(
    user_create: UserCreate,
    user_service: BaseUserService = Depends(Provide[Container.user_service]),
) -> UserResponse:
    print(f"user_service: {user_service}")
    saved_user = user_service.register_user(user_create)
    return saved_user
