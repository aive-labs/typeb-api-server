from src.payment.routes.dto.response.subscription_history_response import (
    SubscriptionHistoryResponse,
)
from src.payment.routes.use_case.get_subscription import GetSubscriptionUseCase
from src.payment.service.port.base_payment_repository import BasePaymentRepository


class GetSubscriptionService(GetSubscriptionUseCase):

    def __init__(self, payment_repository: BasePaymentRepository):
        self.payment_repository = payment_repository

    def get_subscription_payment_history(self, db) -> list[SubscriptionHistoryResponse]:
        subscription_payment = self.payment_repository.get_subscription_payment_history(db)
        return [
            SubscriptionHistoryResponse.from_payment(payment) for payment in subscription_payment
        ]
