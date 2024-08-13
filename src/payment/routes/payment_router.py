from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from src.auth.utils.permission_checker import get_permission_checker
from src.core.container import Container
from src.core.db_dependency import get_db
from src.payment.routes.dto.request.payment_request import (
    PaymentAuthorizationRequestData,
)
from src.payment.routes.dto.request.pre_data_for_validation import PreDataForValidation
from src.payment.routes.use_case.payment import PaymentUseCase
from src.payment.routes.use_case.save_pre_data_for_validation import (
    SavePreDataForValidation,
)

payment_router = APIRouter(
    tags=["Payment"],
)


@payment_router.post("/one-time/pre-validate", status_code=status.HTTP_204_NO_CONTENT)
@inject
def save_pre_data_for_validation(
    pre_data_for_validation: PreDataForValidation,
    user=Depends(get_permission_checker(required_permissions=[])),
    db: Session = Depends(get_db),
    save_pre_data_for_validation_service: SavePreDataForValidation = Depends(
        Provide[Container.save_pre_data_for_validation_service]
    ),
):
    save_pre_data_for_validation_service.save_pre_data_for_validation(
        pre_data_for_validation, user, db
    )


@payment_router.post("/one-time", status_code=status.HTTP_204_NO_CONTENT)
@inject
def one_time_payment_authorization_request(
    payment_authorization_data: PaymentAuthorizationRequestData,
    user=Depends(get_permission_checker(required_permissions=[])),
    db: Session = Depends(get_db),
    one_time_payment_service: PaymentUseCase = Depends(
        Provide[Container.save_pre_data_for_validation_service]
    ),
):
    pass
