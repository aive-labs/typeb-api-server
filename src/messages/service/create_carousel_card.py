from fastapi import UploadFile
from sqlalchemy.orm import Session

from src.core.transactional import transactional
from src.messages.routes.dto.request.kakao_carousel_card_request import (
    KakaoCarouselCardRequest,
)
from src.messages.routes.dto.response.kakao_carousel_card_response import (
    KakaoCarouselCardResponse,
)
from src.messages.routes.port.create_carousel_card_usecase import (
    CreateCarouselCardUseCase,
)
from src.messages.service.port.base_message_repository import BaseMessageRepository
from src.users.domain.user import User


class CreateCarouselCard(CreateCarouselCardUseCase):

    def __init__(self, message_repository: BaseMessageRepository):
        self.message_repository = message_repository

    @transactional
    def create_carousel_card(
        self, file: UploadFile, carousel_card: KakaoCarouselCardRequest, user: User, db: Session
    ) -> KakaoCarouselCardResponse:
        saved_carousel_card = self.message_repository.save_carousel_card(carousel_card, user, db)
        return KakaoCarouselCardResponse(**saved_carousel_card.model_dump())
