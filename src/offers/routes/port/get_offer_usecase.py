from abc import ABC, abstractmethod

from sqlalchemy.orm import Session

from src.offers.routes.dto.response.offer_response import OfferResponse
from src.users.domain.user import User


class GetOfferUseCase(ABC):

    @abstractmethod
    async def get_offers(
        self, based_on, sort_by, start_date, end_date, query, user: User, db: Session
    ) -> list[OfferResponse]:
        pass

    # @abstractmethod
    # def get_offer_detail(self, offer_id) -> OfferDetailResponse:
    #     pass
