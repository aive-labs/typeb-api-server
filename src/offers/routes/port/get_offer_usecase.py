from abc import ABC, abstractmethod

from sqlalchemy.orm import Session

from src.core.transactional import transactional
from src.offers.routes.dto.response.offer_detail_response import OfferDetailResponse
from src.offers.routes.dto.response.offer_response import OfferResponse
from src.users.domain.user import User


class GetOfferUseCase(ABC):

    @transactional
    @abstractmethod
    async def get_offers(
        self, based_on, sort_by, start_date, end_date, query, user: User, db: Session
    ) -> list[OfferResponse]:
        pass

    @abstractmethod
    def get_offer_detail(self, coupon_no, db: Session) -> OfferDetailResponse:
        pass

    @abstractmethod
    def get_offer_count(self, db: Session) -> int:
        pass
