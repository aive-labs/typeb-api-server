from sqlalchemy.orm import Session

from src.core.exceptions.exceptions import NotFoundException
from src.payment.domain.subscription import Subscription, SubscriptionPlan
from src.payment.infra.entity.subscription_entity import (
    SubscriptionEntity,
    SubscriptionPlanEntity,
)
from src.payment.service.port.base_subscription_repository import (
    BaseSubscriptionRepository,
)


class SubscriptionRepository(BaseSubscriptionRepository):

    def get_my_subscription(self, db: Session) -> Subscription | None:
        entity = db.query(SubscriptionEntity).first()

        if not entity:
            return None

        return Subscription.from_model(entity)

    def find_by_name(self, order_name, db: Session) -> SubscriptionPlan:
        entity = (
            db.query(SubscriptionPlanEntity)
            .filter(SubscriptionPlanEntity.name == order_name)
            .first()
        )

        if not entity:
            raise NotFoundException(detail={"message": "해당 요금제는 존재하지 않습니다."})

        return SubscriptionPlan(
            id=entity.id, name=entity.name, price=entity.price, description=entity.description
        )

    def register_subscription(self, new_subscription: Subscription, db: Session) -> Subscription:
        subscription_plan_entity = SubscriptionPlanEntity(
            id=new_subscription.plan.id,
            name=new_subscription.plan.name,
            price=new_subscription.plan.price,
        )

        entity = SubscriptionEntity(
            plan_id=new_subscription.plan_id,
            status=new_subscription.status,
            start_date=new_subscription.start_date,
            end_date=new_subscription.end_date,
            auto_renewal=new_subscription.auto_renewal,
            last_payment_date=new_subscription.last_payment_date,
            created_by=new_subscription.created_by,
            updated_by=new_subscription.created_by,
            plan=subscription_plan_entity,
        )
        db.merge(entity)
        db.flush()

        return Subscription.model_validate(entity)

    def update_status(self, my_subscription: Subscription, new_status: str, db: Session):
        db.query(SubscriptionEntity).filter(SubscriptionEntity.id == my_subscription.id).update(
            {SubscriptionEntity.status: new_status}
        )
        db.flush()

    def get_plans(self, db) -> list[SubscriptionPlan]:
        entities = db.query(SubscriptionPlanEntity).all()
        return [SubscriptionPlan.model_validate(entity) for entity in entities]

    def update_subscription(self, update_subscription, db: Session) -> Subscription:
        subscription_plan_entity = SubscriptionPlanEntity(
            id=update_subscription.plan.id,
            name=update_subscription.plan.name,
            price=update_subscription.plan.price,
        )

        entity = SubscriptionEntity(
            id=update_subscription.id,
            plan_id=update_subscription.plan_id,
            status=update_subscription.status,
            start_date=update_subscription.start_date,
            end_date=update_subscription.end_date,
            auto_renewal=update_subscription.auto_renewal,
            last_payment_date=update_subscription.last_payment_date,
            created_by=update_subscription.created_by,
            updated_by=update_subscription.created_by,
            plan=subscription_plan_entity,
        )
        db.merge(entity)
        db.flush()

        return Subscription.model_validate(entity)
