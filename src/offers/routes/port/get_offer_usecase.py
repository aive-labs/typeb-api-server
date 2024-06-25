from abc import ABC, abstractmethod

from src.offers.routes.dto.offer_response import OfferResponse


class GetOfferUseCase(ABC):

    @abstractmethod
    def get_offers(
        self, based_on, sort_by, start_date, end_date, query
    ) -> list[OfferResponse]:
        pass

    @abstractmethod
    def get_offer_detail(self, offer_id):
        pass
