from src.offers.infra.offer_repository import OfferRepository
from src.offers.routes.dto.response.offer_detail_response import OfferDetailResponse
from src.offers.routes.dto.response.offer_response import OfferResponse
from src.offers.routes.port.get_offer_usecase import GetOfferUseCase


class GetOfferService(GetOfferUseCase):

    def __init__(self, offer_repository: OfferRepository):
        self.offer_repository = offer_repository

    def get_offers(
        self, based_on, sort_by, start_date, end_date, query
    ) -> list[OfferResponse]:
        offers = self.offer_repository.get_all_offers(
            based_on, sort_by, start_date, end_date, query
        )
        return [OfferResponse.from_model(offer) for offer in offers]

    def get_offer_detail(self, offer_key) -> OfferDetailResponse:
        return self.offer_repository.get_offer_detail(offer_key)
