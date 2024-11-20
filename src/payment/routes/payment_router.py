from datetime import datetime
from typing import Optional

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.orm import Session

from src.auth.utils.permission_checker import get_permission_checker
from src.common.pagination.pagination_response import PaginationResponse
from src.core.container import Container
from src.core.db_dependency import get_db
from src.payment.routes.dto.request.cafe24_order_request import Cafe24OrderRequest
from src.payment.routes.dto.request.deposit_without_account import DepositWithoutAccount
from src.payment.routes.dto.request.payment_request import (
    PaymentRequest,
)
from src.payment.routes.dto.request.pre_data_for_validation import PreDataForValidation
from src.payment.routes.dto.response.card_response import CardResponse
from src.payment.routes.dto.response.credit_history_response import (
    CreditHistoryResponse,
)
from src.payment.routes.dto.response.dynamic_subscription_plans import (
    DynamicSubscriptionPlans,
)
from src.payment.routes.dto.response.key_response import KeyResponse
from src.payment.routes.dto.response.remaining_credit import (
    RemainingCreditResponse,
)
from src.payment.routes.dto.response.subscription_history_response import (
    SubscriptionHistoryResponse,
)
from src.payment.routes.use_case.change_card_to_primary_usecase import (
    ChangeCardToPrimaryUseCase,
)
from src.payment.routes.use_case.delete_card import DeleteCardUseCase
from src.payment.routes.use_case.deposit_without_account_usecase import (
    DepositWithoutAccountUseCase,
)
from src.payment.routes.use_case.get_card_usecase import GetCardUseCase
from src.payment.routes.use_case.get_credit import GetCreditUseCase
from src.payment.routes.use_case.get_payment import CustomerKeyUseCase
from src.payment.routes.use_case.get_subscription import GetSubscriptionUseCase
from src.payment.routes.use_case.invoice_download_usecase import InvoiceDownloadUseCase
from src.payment.routes.use_case.payment import PaymentUseCase
from src.payment.routes.use_case.save_pre_data_for_validation import (
    SavePreDataForValidation,
)
from src.payment.service.toss_uuid_key_generator import TossUUIDKeyGenerator

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
    payment_authorization_data: PaymentRequest,
    user=Depends(get_permission_checker(required_permissions=[])),
    db: Session = Depends(get_db),
    one_time_payment_service: PaymentUseCase = Depends(Provide[Container.one_time_payment_service]),
):
    await one_time_payment_service.exec(user, db, payment_authorization_data)


@payment_router.post("/billing", status_code=status.HTTP_204_NO_CONTENT)
@inject
async def billing_payment(
    payment_authorization_data: PaymentRequest,
    user=Depends(get_permission_checker(required_permissions=[])),
    db: Session = Depends(get_db),
    billing_payment_service: PaymentUseCase = Depends(Provide[Container.billing_payment_service]),
):
    await billing_payment_service.exec(user, db, payment_authorization_data)


@payment_router.post("/billing/issue", status_code=status.HTTP_204_NO_CONTENT)
@inject
async def billing_payment_authorization_request(
    payment_authorization_data: PaymentRequest,
    user=Depends(get_permission_checker(required_permissions=[])),
    db: Session = Depends(get_db),
    issue_billing_service: PaymentUseCase = Depends(Provide[Container.issue_billing_service]),
):
    await issue_billing_service.exec(user, db, payment_authorization_data)


@payment_router.get("/cards")
@inject
def get_cards(
    user=Depends(get_permission_checker(required_permissions=[])),
    db: Session = Depends(get_db),
    get_card_service: GetCardUseCase = Depends(Provide[Container.get_card_service]),
) -> list[CardResponse]:
    return get_card_service.exec(db)


@payment_router.patch("/cards/{card_id}/primary", status_code=status.HTTP_204_NO_CONTENT)
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


@payment_router.get("/credit")
@inject
def get_remind_credit(
    user=Depends(get_permission_checker(required_permissions=[])),
    db: Session = Depends(get_db),
    get_credit_service: GetCreditUseCase = Depends(Provide[Container.get_credit_service]),
) -> RemainingCreditResponse:
    credit = get_credit_service.get_credit(db)
    return RemainingCreditResponse(remaining_credit_amount=credit)


@payment_router.get("/credit/history")
@inject
def get_credit_history(
    based_on="created_at",
    sort_by="desc",
    query: Optional[str] = None,
    current_page: int = 1,
    per_page: int = 10,
    user=Depends(get_permission_checker(required_permissions=[])),
    db: Session = Depends(get_db),
    get_credit_service: GetCreditUseCase = Depends(Provide[Container.get_credit_service]),
) -> PaginationResponse[CreditHistoryResponse]:
    return get_credit_service.get_credit_history(
        db=db,
        based_on=based_on,
        sort_by=sort_by,
        current_page=current_page,
        per_page=per_page,
    )


@payment_router.get("/subscription/history")
@inject
def get_subscription_history(
    based_on="created_at",
    sort_by="desc",
    query: Optional[str] = None,
    current_page: int = 1,
    per_page: int = 10,
    user=Depends(get_permission_checker(required_permissions=[])),
    db: Session = Depends(get_db),
    get_subscription_service: GetSubscriptionUseCase = Depends(
        Provide[Container.get_subscription_service]
    ),
) -> PaginationResponse[SubscriptionHistoryResponse]:
    return get_subscription_service.get_subscription_payment_history(
        db=db,
        based_on=based_on,
        sort_by=sort_by,
        current_page=current_page,
        per_page=per_page,
    )


@payment_router.get("/key")
@inject
def get_key(
    type: str | None = None,
    user=Depends(get_permission_checker(required_permissions=[])),
    db: Session = Depends(get_db),
    customer_key_service: CustomerKeyUseCase = Depends(Provide[Container.customer_key_service]),
) -> KeyResponse:
    if type == "order":
        key = TossUUIDKeyGenerator.generate(type)
    elif type == "customer":
        key = customer_key_service.get_customer_key(user.mall_id, db)
        if key is None:
            key = TossUUIDKeyGenerator.generate(user.mall_id)
            customer_key_service.save_customer_key(user, key, db=db)
    else:
        key = TossUUIDKeyGenerator.generate()

    return KeyResponse(key=key)


@payment_router.get("/subscription-plans")
@inject
def get_subscription_plans(
    user=Depends(get_permission_checker(required_permissions=[])),
    db: Session = Depends(get_db),
    get_subscription_service: GetSubscriptionUseCase = Depends(
        Provide[Container.get_subscription_service]
    ),
) -> DynamicSubscriptionPlans:
    return get_subscription_service.get_plans(db)


@payment_router.post("/deposit", status_code=status.HTTP_201_CREATED)
@inject
def deposit_without_bank_account(
    deposit_request: DepositWithoutAccount,
    user=Depends(get_permission_checker(required_permissions=[])),
    db: Session = Depends(get_db),
    deposit_service: DepositWithoutAccountUseCase = Depends(Provide[Container.deposit_service]),
):
    deposit_service.exec(deposit_request, user, db=db)


@payment_router.post(
    "/deposit/{pending_deposit_id}/complete", status_code=status.HTTP_204_NO_CONTENT
)
@inject
def deposit_complete(
    pending_deposit_id: int,
    user=Depends(get_permission_checker(required_permissions=[])),
    db: Session = Depends(get_db),
    deposit_service: DepositWithoutAccountUseCase = Depends(Provide[Container.deposit_service]),
):
    deposit_service.complete(pending_deposit_id, user, db=db)


@payment_router.get("/invoice/{credit_history_id}")
@inject
def download_invoice(
    credit_history_id: str,
    user=Depends(get_permission_checker(required_permissions=[])),
    db: Session = Depends(get_db),
    invoice_download_service: InvoiceDownloadUseCase = Depends(
        Provide[Container.invoice_download_service]
    ),
):
    pdf_file = invoice_download_service.exec(credit_history_id, user, db)
    download_date = datetime.today().strftime("%Y%m%d")

    return Response(
        pdf_file,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=invoice_{download_date}.pdf"},
    )


@payment_router.post("/cafe24-order")
@inject
async def create_cafe24_order(
    cafe24_order_request: Cafe24OrderRequest,
    user=Depends(get_permission_checker(required_permissions=[])),
    db: Session = Depends(get_db),
    cafe24_payment_service: PaymentUseCase = Depends(Provide[Container.cafe24_payment_service]),
):
    payment_request = PaymentRequest(
        order_id=cafe24_order_request.order_id,
        order_name=cafe24_order_request.order_name,
        amount=cafe24_order_request.order_amount,
        product_type=cafe24_order_request.product_type,
    )

    await cafe24_payment_service.exec(user, db, payment_request)
