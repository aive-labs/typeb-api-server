from sqlalchemy.orm import Session

from src.core.exceptions.exceptions import NotFoundException
from src.payment.domain.subscription import Subscription
from src.payment.infra.entity.subscription_entity import SubscriptionEntity
from src.payment.service.port.base_subscription_repository import (
    BaseSubscriptionRepository,
)


class SubscriptionRepository(BaseSubscriptionRepository):
    def get_my_subscription(self, db: Session) -> Subscription:
        entity = db.query(SubscriptionEntity).first()

        if not entity:
            raise NotFoundException("구독 중인 요금제가 없습니다.")

        return Subscription.from_model(entity)
