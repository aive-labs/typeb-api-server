from sqlalchemy.orm import Session

from src.core.transactional import transactional
from src.messages.routes.dto.response.kakao_carousel_card_response import (
    KakaoCarouselCardResponse,
)
from src.messages.routes.port.delete_carousel_card_usecase import (
    DeleteCarouselCardUseCase,
)
from src.messages.service.port.base_message_repository import BaseMessageRepository


class DeleteCarouselCard(DeleteCarouselCardUseCase):

    def __init__(self, message_repository: BaseMessageRepository):
        self.message_repository = message_repository

    @transactional
    def exec(self, carousel_card_id, db: Session) -> list[KakaoCarouselCardResponse]:
        set_group_msg_seq = self.message_repository.delete_carousel_card(carousel_card_id, db)
        kakao_carousel_cards = self.message_repository.get_carousel_cards_by_set_group_msg_seq(
            set_group_msg_seq=set_group_msg_seq, db=db
        )

        return [KakaoCarouselCardResponse(**card.model_dump()) for card in kakao_carousel_cards]
