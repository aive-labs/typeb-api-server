from abc import ABC, abstractmethod

from fastapi import UploadFile
from sqlalchemy.orm import Session

from src.core.transactional import transactional
from src.messages.routes.dto.request.kakao_carousel_card_request import (
    KakaoCarouselCardRequest,
)
from src.messages.routes.dto.response.kakao_carousel_card_response import (
    KakaoCarouselCardResponse,
)
from src.users.domain.user import User


class CreateCarouselCardUseCase(ABC):

    @transactional
    @abstractmethod
    def create_carousel_card(
        self,
        file: UploadFile,
        carousel_card_request: KakaoCarouselCardRequest,
        user: User,
        db: Session,
    ) -> KakaoCarouselCardResponse:
        pass
