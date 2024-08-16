from abc import ABC, abstractmethod

from src.payment.domain.subscription import SubscriptionPlan
from src.payment.routes.dto.response.subscription_history_response import (
    SubscriptionHistoryResponse,
)


class GetSubscriptionUseCase(ABC):

    @abstractmethod
    def get_subscription_payment_history(self, db) -> list[SubscriptionHistoryResponse]:
        pass

    @abstractmethod
    def get_plans(self, db) -> list[SubscriptionPlan]:
        pass
