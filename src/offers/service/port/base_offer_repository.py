from abc import ABC, abstractmethod

from sqlalchemy.orm import Session

from src.offers.domain.offer import Offer


class BaseOfferRepository(ABC):

    @abstractmethod
    def get_offer(self, coupon_no, db: Session) -> Offer:
        pass

    @abstractmethod
    def get_offer_detail(self, coupon_no, db: Session) -> Offer:
        pass

    @abstractmethod
    def get_offer_by_id(self, coupon_no: str, db: Session) -> Offer:
        pass
