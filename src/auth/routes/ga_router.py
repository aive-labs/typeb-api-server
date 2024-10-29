from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from src.auth.routes.port.base_ga_service import BaseGAIntegrationService
from src.auth.utils.permission_checker import get_permission_checker
from src.core.container import Container
from src.core.db_dependency import get_db

ga_router = APIRouter(
    tags=["Google Analytics"],
)


@ga_router.post("/")
@inject
def execute_ga_integration(
    mall_id: str,
    ga_service: BaseGAIntegrationService = Depends(Provide[Container.cafe24_service]),
    user=Depends(get_permission_checker(required_permissions=[])),
    db: Session = Depends(get_db),
):
    ga_service.execute_ga_automation(mall_id, user, db)
