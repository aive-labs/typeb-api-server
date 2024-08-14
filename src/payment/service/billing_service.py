from sqlalchemy.orm import Session

from src.payment.domain.card import Card
from src.payment.infra.payment_repository import PaymentRepository
from src.payment.routes.dto.request.payment_request import (
    PaymentAuthorizationRequestData,
)
from src.payment.routes.use_case.issue_billing_key import IssueBillingKeyUseCase
from src.payment.routes.use_case.payment_gateway import PaymentGateway
from src.users.domain.user import User


class IssueBillingService(IssueBillingKeyUseCase):

    def __init__(self, payment_repository: PaymentRepository, payment_gateway: PaymentGateway):
        self.payment_repository = payment_repository
        self.payment_gateway = payment_gateway

    async def issue_billing_key(
        self, payment_data: PaymentAuthorizationRequestData, user: User, db: Session
    ):
        response = await self.payment_gateway.request_billing_key(payment_data)
        card = Card.from_toss_payment_response(response, user)

        is_not_exist_primary_card = self.payment_repository.is_not_exist_primary_card(db)

        if is_not_exist_primary_card:
            card.change_primary_card()

        self.payment_repository.save_billing_key(card, db)
