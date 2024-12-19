import math

from sqlalchemy.orm import Session

from src.common.pagination.pagination_base import PaginationBase
from src.common.pagination.pagination_response import PaginationResponse
from src.common.service.port.base_common_repository import BaseCommonRepository
from src.common.utils.get_round_up_to_then_thousand import (
    round_up_to_nearest_ten_thousand,
)
from src.payment.domain.subscription import Subscription
from src.payment.model.response.dynamic_subscription_plans import (
    DynamicSubscriptionPlans,
)
from src.payment.model.response.subscription_history_response import (
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
        common_repository: BaseCommonRepository,
    ):
        self.payment_repository = payment_repository
        self.subscription_repository = subscription_repository
        self.common_repository = common_repository

    def get_subscription_payment_history(
        self, db: Session, based_on, sort_by, current_page, per_page
    ) -> PaginationResponse[SubscriptionHistoryResponse]:
        subscription_payment = self.payment_repository.get_subscription_payment_history(
            db, current_page, per_page
        )
        responses = [
            SubscriptionHistoryResponse.from_payment(payment) for payment in subscription_payment
        ]

        all_count = self.payment_repository.get_all_subscription_count(db)

        pagination = PaginationBase(
            total=all_count,
            per_page=per_page,
            current_page=current_page,
            total_page=math.ceil(all_count / per_page),
        )

        return PaginationResponse[SubscriptionHistoryResponse](
            items=responses, pagination=pagination
        )

    def get_plans(self, db) -> DynamicSubscriptionPlans:
        plans = self.subscription_repository.get_plans(db)

        all_customer_count = self.common_repository.get_all_customer_count(db)

        all_customer_count = all_customer_count if all_customer_count > 0 else 1
        estimated_customer_count_for_pricing = round_up_to_nearest_ten_thousand(all_customer_count)

        for plan in plans:
            plan.set_price(estimated_customer_count_for_pricing)

        return DynamicSubscriptionPlans(customer_count=all_customer_count, subscription_plans=plans)

    def get_my_subscription(self, db) -> Subscription | None:
        return self.subscription_repository.get_my_subscription(db)
