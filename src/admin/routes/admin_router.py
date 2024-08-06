from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from src.admin.routes.dto.response.personal_variable_response import (
    PersonalVariableResponse,
)
from src.admin.routes.port.get_personal_variables_usecase import (
    GetPersonalVariablesUseCase,
)
from src.auth.utils.permission_checker import get_permission_checker
from src.core.container import Container
from src.core.db_dependency import get_db

admin_router = APIRouter(tags=["Admin"])


@admin_router.get("/personal-variable")
@inject
def get_personal_variable(
    user=Depends(get_permission_checker(required_permissions=[])),
    db: Session = Depends(get_db),
    get_personal_variables_service: GetPersonalVariablesUseCase = Depends(
        Provide[Container.get_personal_variables_service]
    ),
) -> list[PersonalVariableResponse]:
    return get_personal_variables_service.get_personal_variable(user, db=db)
