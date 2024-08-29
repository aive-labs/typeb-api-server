from datetime import datetime, timezone

from dateutil.relativedelta import relativedelta
from pydantic import BaseModel

from src.payment.infra.entity.subscription_entity import SubscriptionEntity
from src.users.domain.user import User


class SubscriptionPlan(BaseModel):
    id: int
    name: str
    price: int
    description: str | None = None

    class Config:
        from_attributes = True

    def set_price(self, customer_count):
        self.price = self.price * customer_count


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

    class Config:
        from_attributes = True

    @staticmethod
    def from_model(model: SubscriptionEntity) -> "Subscription":
        subscription_plan = SubscriptionPlan(
            id=model.plan.id,
            name=model.plan.name,
            price=model.plan.price,
            description=model.plan.description,
        )

        subscription = Subscription(
            id=model.id,
            plan_id=model.plan_id,
            status=model.status,
            start_date=model.start_date,
            end_date=model.end_date,
            auto_renewal=False,
            last_payment_date=model.last_payment_date,
            created_by=model.created_by,
            created_at=model.created_at,
            plan=subscription_plan,
        )

        return subscription

    @staticmethod
    def with_status(plan: SubscriptionPlan, status: str, user: User) -> "Subscription":
        return Subscription(
            plan_id=plan.id,
            status=status,
            start_date=datetime.now(timezone.utc),
            end_date=datetime.now(timezone.utc) + relativedelta(months=1),
            auto_renewal=False,
            last_payment_date=datetime.now(timezone.utc),
            created_by=str(user.user_id),
            created_at=datetime.now(timezone.utc),
            plan=plan,
        )

    def extend_end_date(self):
        self.end_date = self.end_date + relativedelta(months=1)

    def is_expired(self):
        if datetime.today().date() > self.end_date.date():
            return True
        return False

    def get_id(self):
        return self.id

    def set_id(self, id):
        self.id = id
