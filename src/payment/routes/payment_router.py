from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from src.auth.utils.permission_checker import get_permission_checker
from src.core.container import Container
from src.core.db_dependency import get_db
from src.payment.domain.card import Card
from src.payment.routes.dto.request.payment_request import (
    PaymentAuthorizationRequestData,
)
from src.payment.routes.dto.request.pre_data_for_validation import PreDataForValidation
from src.payment.routes.use_case.change_card_to_primary_usecase import (
    ChangeCardToPrimaryUseCase,
)
from src.payment.routes.use_case.delete_card import DeleteCardUseCase
from src.payment.routes.use_case.get_card_usecase import GetCardUseCase
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
async def one_time_payment_authorization_request(
    payment_authorization_data: PaymentAuthorizationRequestData,
    user=Depends(get_permission_checker(required_permissions=[])),
    db: Session = Depends(get_db),
    one_time_payment_service: PaymentUseCase = Depends(Provide[Container.one_time_payment_service]),
):
    await one_time_payment_service.exec(payment_authorization_data, user, db)


@payment_router.post("/billing", status_code=status.HTTP_204_NO_CONTENT)
@inject
async def billing_payment_authorization_request(
    payment_authorization_data: PaymentAuthorizationRequestData,
    user=Depends(get_permission_checker(required_permissions=[])),
    db: Session = Depends(get_db),
    issue_billing_service: PaymentUseCase = Depends(Provide[Container.issue_billing_service]),
):
    await issue_billing_service.exec(payment_authorization_data, user, db)


@payment_router.get("/cards")
@inject
def get_cards(
    user=Depends(get_permission_checker(required_permissions=[])),
    db: Session = Depends(get_db),
    get_card_service: GetCardUseCase = Depends(Provide[Container.get_card_service]),
) -> list[Card]:
    return get_card_service.exec(user, db)


@payment_router.patch("/cards/{card_id}/is_primary", status_code=status.HTTP_204_NO_CONTENT)
@inject
def change_card_status_to_primary(
    card_id: int,
    user=Depends(get_permission_checker(required_permissions=[])),
    db: Session = Depends(get_db),
    change_card_to_primary_service: ChangeCardToPrimaryUseCase = Depends(
        Provide[Container.change_card_to_primary_service]
    ),
):
    change_card_to_primary_service.exec(card_id, user, db=db)


@payment_router.delete("/cards/{card_id}", status_code=status.HTTP_204_NO_CONTENT)
@inject
def delete_card(
    card_id: int,
    user=Depends(get_permission_checker(required_permissions=[])),
    db: Session = Depends(get_db),
    delete_card_service: DeleteCardUseCase = Depends(Provide[Container.delete_card_service]),
):
    delete_card_service.exec(card_id, user, db=db)
