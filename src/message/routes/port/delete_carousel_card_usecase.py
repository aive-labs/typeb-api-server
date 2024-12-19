from abc import ABC, abstractmethod

from sqlalchemy.orm import Session

from src.core.transactional import transactional
from src.message.routes.dto.response.kakao_carousel_card_response import (
    KakaoCarouselCardResponse,
)


class DeleteCarouselCardUseCase(ABC):

    @transactional
    @abstractmethod
    def exec(self, carousel_card_id, db: Session) -> list[KakaoCarouselCardResponse]:
        pass
