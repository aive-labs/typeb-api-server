from fastapi import UploadFile
from sqlalchemy.orm import Session

from src.campaign.routes.port.upload_image_for_message_usecase import (
    UploadImageForMessageUseCase,
)
from src.common.utils.get_env_variable import get_env_variable
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
        self.cloud_front_url = get_env_variable("cloud_front_asset_url")

    async def create_carousel_card(
        self,
        file: UploadFile,
        carousel_card_request: KakaoCarouselCardRequest,
        user: User,
        db: Session,
    ) -> KakaoCarouselCardResponse:
        carousel_card = KakaoCarouselCard(**carousel_card_request.model_dump())
        carousel_image_links = await self.upload_image_for_message.upload_for_carousel(
            file, carousel_card, user, db
        )
        carousel_card.set_image_url(
            carousel_image_links.kakao_image_link, carousel_image_links.s3_image_path
        )
        saved_carousel_card = self.message_repository.save_carousel_card(carousel_card, user, db)

        response = KakaoCarouselCardResponse(**saved_carousel_card.model_dump())
        response.set_image_url(f"{self.cloud_front_url}/{response.s3_image_path}")

        db.commit()

        return response
