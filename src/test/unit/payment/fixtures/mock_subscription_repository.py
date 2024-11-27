from unittest.mock import MagicMock

from src.payment.domain.subscription import SubscriptionPlan, Subscription
from src.payment.service.port.base_subscription_repository import BaseSubscriptionRepository


def get_mock_subscription_repository():
    mock_repository = MagicMock(spec_set=BaseSubscriptionRepository)

    subscription: Subscription | None = None

    def get_plans(db) -> list[SubscriptionPlan]:
        return [
            SubscriptionPlan(
                id=1,
                name="1개월",
                price=30000,
                description="한달 일별캠페인의 집행 금액 평균의 합계가 100만원 이하입니다.",
            )
        ]

    def get_my_subscription(db) -> Subscription | None:
        return subscription

    def register_subscription(new_subscription, db):
        subscription = new_subscription

    def update_subscription(new_subscription, db):
        pass

    mock_repository.get_my_subscription.side_effect = get_my_subscription
    mock_repository.get_plans.side_effect = get_plans
    mock_repository.register_subscription.side_effect = register_subscription
    mock_repository.update_subscription.side_effect = update_subscription

    return mock_repository
