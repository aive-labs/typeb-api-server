from pydantic import BaseModel

from src.payment.domain.subscription import SubscriptionPlan


class DynamicSubscriptionPlans(BaseModel):
    customer_count: int
    subscription_plans: list[SubscriptionPlan]
