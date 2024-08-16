from abc import ABC, abstractmethod

from sqlalchemy.orm import Session

from src.payment.domain.subscription import Subscription


class BaseSubscriptionRepository(ABC):

    @abstractmethod
    def get_my_subscription(self, db: Session) -> Subscription:
        pass
