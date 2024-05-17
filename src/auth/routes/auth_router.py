import os

from auth.routes.dto.response.token_response import TokenResponse
from auth.service.auth_service import AuthService
from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm

print(os.getcwd())

from core.container import Container

auth_router = APIRouter(
    tags=["auth"],
)


@auth_router.post("/login")
@inject  # UserService 주입
def sign_up(
    form_data: OAuth2PasswordRequestForm=Depends(),
    auth_service: AuthService = Depends(dependency=Provide[Container.auth_service]),
) -> TokenResponse:
    print(f"auth_service: {auth_service}")

    login_id = form_data.username
    password= form_data.password

    token_response = auth_service.login(login_id, password)
    return token_response


@auth_router.post("/token")
@inject  # TokenService 주입
def get_access_token(
    refresh_token: str,
    auth_service: AuthService = Depends(Provide[Container.auth_service]),
) -> TokenResponse:

    # user: get_me
    auth_service.get_new_token(refresh_token=refresh_token)

    return TokenResponse(access_token='', token_type='', refresh_token='', expires_in=10)
