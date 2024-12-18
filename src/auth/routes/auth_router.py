from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, BackgroundTasks, Depends, status
from sqlalchemy.orm import Session

from src.auth.routes.dto.request.cafe24_token_request import OauthAuthenticationRequest
from src.auth.routes.dto.response.cafe24_app_execution_link import (
    Cafe24AppExecutionLink,
)
from src.auth.routes.port.base_ga_service import BaseGAIntegrationService
from src.auth.routes.port.base_oauth_service import BaseOauthService
from src.auth.utils.permission_checker import get_permission_checker
from src.core.container import Container
from src.core.db_dependency import get_db

auth_router = APIRouter(
    tags=["Auth"],
)


@auth_router.get("/oauth/cafe24")
@inject
def get_cafe24_authentication_url(
    mall_id: str,
    background_tasks: BackgroundTasks,
    cafe24_service: BaseOauthService = Depends(Provide[Container.cafe24_service]),
    ga_service: BaseGAIntegrationService = Depends(Provide[Container.ga_service]),
    user=Depends(get_permission_checker(required_permissions=[])),
    db: Session = Depends(get_db),
) -> str:
    authentication_url = cafe24_service.get_oauth_authentication_url(mall_id, user, db=db)

    user.mall_id = mall_id
    # background_tasks.add_task(ga_service.execute_ga_automation, user, db)

    return authentication_url


@auth_router.post("/oauth/cafe24/token", status_code=status.HTTP_201_CREATED)
@inject
async def get_cafe24_access_token(
    cafe_authentication_request: OauthAuthenticationRequest,
    cafe24_service: BaseOauthService = Depends(Provide[Container.cafe24_service]),
    user=Depends(get_permission_checker(required_permissions=[])),
    db: Session = Depends(get_db),
) -> None:
    await cafe24_service.get_oauth_access_token(cafe_authentication_request, db=db)


@auth_router.get("/oauth/cafe24/install")
@inject
def get_cafe24_authentication_url_when_install(
    mall_id: str,
    cafe24_service: BaseOauthService = Depends(Provide[Container.cafe24_service]),
) -> str:
    authentication_url = cafe24_service.get_oauth_authentication_url_when_install(mall_id)

    return authentication_url


@auth_router.post("/oauth/cafe24/install/token", status_code=status.HTTP_201_CREATED)
@inject
async def get_cafe24_access_token_when_install(
    cafe_authentication_request: OauthAuthenticationRequest,
    cafe24_service: BaseOauthService = Depends(Provide[Container.cafe24_service]),
) -> None:
    await cafe24_service.get_oauth_access_token_when_install(cafe_authentication_request)


@auth_router.post("/oauth/cafe24/app-link/validation", status_code=status.HTTP_200_OK)
@inject
def validate_app_execution_link(
    cafe24_app_execution_link: Cafe24AppExecutionLink,
    cafe24_service: BaseOauthService = Depends(Provide[Container.cafe24_service]),
) -> None:
    cafe24_service.get_app_execution_validation_check(
        cafe24_app_execution_link.url.unicode_string()
    )
