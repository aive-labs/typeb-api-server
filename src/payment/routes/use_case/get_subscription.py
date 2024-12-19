from abc import ABC, abstractmethod

from sqlalchemy.orm import Session

from src.common.pagination.pagination_response import PaginationResponse
from src.payment.domain.subscription import Subscription
from src.payment.model.response.dynamic_subscription_plans import (
    DynamicSubscriptionPlans,
)
from src.payment.model.response.subscription_history_response import (
    SubscriptionHistoryResponse,
)


class GetSubscriptionUseCase(ABC):

    @abstractmethod
    def get_subscription_payment_history(
        self, db: Session, based_on, sort_by, current_page, per_page
    ) -> PaginationResponse[SubscriptionHistoryResponse]:
        pass

    @abstractmethod
    def get_plans(self, db) -> DynamicSubscriptionPlans:
        pass

    @abstractmethod
    def get_my_subscription(self, db) -> Subscription | None:
        pass
