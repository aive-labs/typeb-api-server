from src.payment.domain.subscription import SubscriptionPlan
from src.payment.routes.dto.response.subscription_history_response import (
    SubscriptionHistoryResponse,
)
from src.payment.routes.use_case.get_subscription import GetSubscriptionUseCase
from src.payment.service.port.base_payment_repository import BasePaymentRepository
from src.payment.service.port.base_subscription_repository import (
    BaseSubscriptionRepository,
)


class GetSubscriptionService(GetSubscriptionUseCase):

    def __init__(
        self,
        payment_repository: BasePaymentRepository,
        subscription_repository: BaseSubscriptionRepository,
    ):
        self.payment_repository = payment_repository
        self.subscription_repository = subscription_repository

    def get_subscription_payment_history(self, db) -> list[SubscriptionHistoryResponse]:
        subscription_payment = self.payment_repository.get_subscription_payment_history(db)
        return [
            SubscriptionHistoryResponse.from_payment(payment) for payment in subscription_payment
        ]

    def get_plans(self, db) -> list[SubscriptionPlan]:
        return self.subscription_repository.get_plans(db)
