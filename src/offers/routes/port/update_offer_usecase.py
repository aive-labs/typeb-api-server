from abc import ABC, abstractmethod

from src.offers.routes.dto.request.offer_update import OfferUpdate
from src.users.domain.user import User


class UpdateOfferUseCase(ABC):

    @abstractmethod
    def update_offer(self, offer_update: OfferUpdate, user: User):
        pass
