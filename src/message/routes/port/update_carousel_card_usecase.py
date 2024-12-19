from abc import ABC, abstractmethod

from fastapi import UploadFile
from sqlalchemy.orm import Session

from src.message.model.request.kakao_carousel_card_request import (
    KakaoCarouselCardRequest,
)
from src.message.model.response.kakao_carousel_card_response import (
    KakaoCarouselCardResponse,
)
from src.user.domain.user import User


class UpdateCarouselCardUseCase(ABC):

    @abstractmethod
    def exec(
        self,
        file: UploadFile,
        carousel_card_request: KakaoCarouselCardRequest,
        user: User,
        db: Session,
    ) -> KakaoCarouselCardResponse:
        pass
