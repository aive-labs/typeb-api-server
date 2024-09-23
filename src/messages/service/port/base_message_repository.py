from abc import ABC, abstractmethod

from sqlalchemy.orm import Session

from src.messages.domain.kakao_carousel_card import KakaoCarouselCard
from src.messages.domain.kakao_carousel_more_link import KakaoCarouselMoreLink
from src.messages.routes.dto.ppurio_message_result import PpurioMessageResult
from src.users.domain.user import User


class BaseMessageRepository(ABC):

    @abstractmethod
    def save_message_result(self, result: PpurioMessageResult, db: Session):
        pass

    @abstractmethod
    def save_carousel_card(
        self, carousel_card: KakaoCarouselCard, user: User, db: Session
    ) -> KakaoCarouselCard:
        pass

    @abstractmethod
    def delete_carousel_card(self, carousel_card_id: int, db: Session):
        pass

    @abstractmethod
    def save_carousel_more_link(self, carousel_more_link: KakaoCarouselMoreLink, db: Session):
        pass

    @abstractmethod
    def get_carousel_card_count(self, set_group_msg_seq, db: Session) -> int:
        pass

    @abstractmethod
    def get_carousel_more_link_id_by_set_group_msg_seq(
        self, set_group_msg_seq, db: Session
    ) -> int | None:
        pass

    @abstractmethod
    def get_carousel_card_by_id(self, id, db) -> KakaoCarouselCard:
        pass
