from fastapi import UploadFile
from sqlalchemy.orm import Session

from src.campaign.routes.port.upload_image_for_message_usecase import (
    UploadImageForMessageUseCase,
)
from src.core.transactional import transactional
from src.messages.domain.kakao_carousel_card import KakaoCarouselCard
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

    def __init__(
        self,
        message_repository: BaseMessageRepository,
        upload_image_for_message: UploadImageForMessageUseCase,
    ):
        self.message_repository = message_repository
        self.upload_image_for_message = upload_image_for_message

    @transactional
    def create_carousel_card(
        self,
        file: UploadFile,
        carousel_card_request: KakaoCarouselCardRequest,
        user: User,
        db: Session,
    ) -> KakaoCarouselCardResponse:
        carousel_card = KakaoCarouselCard(**carousel_card_request.model_dump())

        image_link = self.upload_image_for_message.upload_for_carousel(
            file, carousel_card.set_group_msg_seq, user, db
        )
        carousel_card.set_image_link(image_link)

        saved_carousel_card = self.message_repository.save_carousel_card(carousel_card, user, db)
        return KakaoCarouselCardResponse(**saved_carousel_card.model_dump())
