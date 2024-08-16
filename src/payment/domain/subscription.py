from datetime import datetime

from pydantic import BaseModel

from src.payment.infra.entity.subscription_entity import SubscriptionEntity


class SubscriptionPlan(BaseModel):
    id: int
    name: str
    price: int


class Subscription(BaseModel):
    id: int | None = None
    plan_id: int
    status: str
    start_date: datetime
    end_date: datetime
    auto_renewal: bool
    last_payment_date: datetime
    created_by: str
    created_at: datetime
    plan: SubscriptionPlan

    @staticmethod
    def from_model(model: SubscriptionEntity) -> "Subscription":
        subscription_plan = SubscriptionPlan(
            id=model.plan.id, name=model.plan.name, price=model.plan.price
        )

        subscription = Subscription(
            id=model.id,
            plan_id=model.plan_id,
            status=model.status,
            start_date=model.start_date,
            end_date=model.end_date,
            auto_renewal=model.auto_renewal,
            last_payment_date=model.last_payment_date,
            created_by=model.created_by,
            created_at=model.created_at,
            plan=subscription_plan,
        )

        return subscription
