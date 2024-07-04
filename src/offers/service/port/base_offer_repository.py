from abc import ABC, abstractmethod

from sqlalchemy.orm import Session

from src.campaign.domain.campaign import Campaign
from src.offers.domain.offer import Offer
from src.offers.domain.offer_details import OfferDetails
from src.users.domain.user import User


class BaseOfferRepository(ABC):

    @abstractmethod
    def get_offer(
        self, offer_id: str, user: User
    ) -> Offer:
        pass

    @abstractmethod
    def get_offer_details(
        self, offer_key: int, user: User
    ) -> OfferDetails:
        pass