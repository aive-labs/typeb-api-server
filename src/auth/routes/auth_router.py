from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from src.auth.routes.dto.request.cafe24_token_request import OauthAuthenticationRequest
from src.auth.routes.dto.response.token_response import TokenResponse
from src.auth.routes.port.base_oauth_service import BaseOauthService
from src.auth.service.auth_service import AuthService
from src.auth.utils.permission_checker import get_permission_checker
from src.core.container import Container
from src.core.database import get_db_session

auth_router = APIRouter(
    tags=["Auth"],
)


@auth_router.post("/token")
@inject  # TokenService 주입
def get_access_token(
    refresh_token: str,
    user=Depends(get_permission_checker(required_permissions=[])),
    db: Session = Depends(get_db_session),
    auth_service: AuthService = Depends(Provide[Container.auth_service]),
) -> TokenResponse:
    # user: get_me
    auth_service.get_new_token(refresh_token=refresh_token, db=db)

    return TokenResponse(
        access_token="", token_type="", refresh_token="", expires_in=10
    )


@auth_router.get("/oauth/cafe24")
@inject
def get_cafe24_authentication_url(
    mall_id: str,
    cafe24_service: BaseOauthService = Depends(Provide[Container.cafe24_service]),
    user=Depends(get_permission_checker(required_permissions=[])),
    db: Session = Depends(get_db_session),
) -> str:
    authentication_url = cafe24_service.get_oauth_authentication_url(
        mall_id, user, db=db
    )
    return authentication_url


@auth_router.post("/oauth/cafe24/token", status_code=status.HTTP_201_CREATED)
@inject
def get_cafe24_access_token(
    cafe_authentication_request: OauthAuthenticationRequest,
    cafe24_service: BaseOauthService = Depends(Provide[Container.cafe24_service]),
    user=Depends(get_permission_checker(required_permissions=[])),
    db: Session = Depends(get_db_session),
) -> None:
    cafe24_service.get_oauth_access_token(cafe_authentication_request, db=db)
