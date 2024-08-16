from abc import ABC, abstractmethod

from src.payment.routes.dto.response.subscription_history_response import (
    SubscriptionHistoryResponse,
)


class GetSubscriptionUseCase(ABC):

    @abstractmethod
    def get_subscription_payment_history(self, db) -> list[SubscriptionHistoryResponse]:
        pass
