from abc import ABC, abstractmethod

from sqlalchemy.orm import Session

from src.payment.domain.subscription import Subscription, SubscriptionPlan


class BaseSubscriptionRepository(ABC):

    @abstractmethod
    def get_my_subscription(self, db: Session) -> Subscription | None:
        pass

    @abstractmethod
    def find_by_name(self, order_name, db: Session) -> SubscriptionPlan:
        pass

    @abstractmethod
    def register_subscription(self, new_subscription, db: Session) -> Subscription:
        pass
