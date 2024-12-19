from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from src.admin.model.outsoring_personal_information_status import (
    OutSourcingPersonalInformationStatus,
)
from src.admin.model.response.personal_variable_response import (
    PersonalVariableResponse,
)
from src.admin.routes.port.base_personal_information_service import (
    BasePersonalInformationService,
)
from src.admin.routes.port.get_personal_variables_usecase import (
    GetPersonalVariablesUseCase,
)
from src.auth.utils.permission_checker import get_permission_checker
from src.main.container import Container
from src.main.db_dependency import get_db

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


@admin_router.get("/personal-information-term/status")
@inject
def get_outsourcing_personal_information_status(
    user=Depends(get_permission_checker(required_permissions=[])),
    personal_information_service: BasePersonalInformationService = Depends(
        Provide[Container.personal_information_service]
    ),
    db: Session = Depends(get_db),
):
    return personal_information_service.get_status(db=db)


@admin_router.patch("/personal-information-term/status", status_code=status.HTTP_204_NO_CONTENT)
@inject
def update_outsourcing_personal_information_status(
    to_status: OutSourcingPersonalInformationStatus,
    user=Depends(get_permission_checker(required_permissions=[])),
    personal_information_service: BasePersonalInformationService = Depends(
        Provide[Container.personal_information_service]
    ),
    db: Session = Depends(get_db),
):
    personal_information_service.update_status(to_status.value, user, db=db)
