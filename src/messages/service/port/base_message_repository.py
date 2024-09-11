from abc import ABC, abstractmethod

from sqlalchemy.orm import Session

from src.messages.domain.kakao_carousel_card import KakaoCarouselCard
from src.messages.routes.dto.ppurio_message_result import PpurioMessageResult
from src.messages.routes.dto.request.kakao_carousel_card_request import (
    KakaoCarouselCardRequest,
)
from src.users.domain.user import User


class BaseMessageRepository(ABC):

    @abstractmethod
    def save_message_result(self, result: PpurioMessageResult, db: Session):
        pass

    @abstractmethod
    def save_carousel_card(
        self, carousel_card: KakaoCarouselCardRequest, user: User, db: Session
    ) -> KakaoCarouselCard:
        pass

    @abstractmethod
    def delete_carousel_card(self, carousel_card_id: int, db: Session):
        pass
