from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from src.auth.routes.dto.response.ga_script_response import GAScriptResponse
from src.auth.routes.port.base_ga_service import BaseGAIntegrationService
from src.auth.utils.permission_checker import get_permission_checker
from src.core.container import Container
from src.core.db_dependency import get_db

ga_router = APIRouter(
    tags=["Google Analytics"],
)


@ga_router.post("")
@inject
async def execute_ga_integration(
    ga_service: BaseGAIntegrationService = Depends(Provide[Container.ga_service]),
    user=Depends(get_permission_checker(required_permissions=[])),
    db: Session = Depends(get_db),
):
    await ga_service.execute_ga_automation(user, db=db)


@ga_router.get("")
@inject
def get_ga_script(
    ga_service: BaseGAIntegrationService = Depends(Provide[Container.ga_service]),
    user=Depends(get_permission_checker(required_permissions=[])),
    db: Session = Depends(get_db),
) -> GAScriptResponse:
    return ga_service.generate_ga_script(user, db=db)
