import math

from sqlalchemy.orm import Session

from src.common.pagination.pagination_base import PaginationBase
from src.common.pagination.pagination_response import PaginationResponse
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

    def get_plans(self, db) -> list[SubscriptionPlan]:
        return self.subscription_repository.get_plans(db)
