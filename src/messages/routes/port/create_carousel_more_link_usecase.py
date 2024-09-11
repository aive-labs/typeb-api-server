from abc import ABC, abstractmethod

from sqlalchemy.orm import Session

from src.core.transactional import transactional
from src.messages.routes.dto.request.kakao_carousel_more_link_request import (
    KakaoCarouselMoreLinkRequest,
)
from src.users.domain.user import User


class CreateCarouselMoreLinkUseCase(ABC):

    @transactional
    @abstractmethod
    def exec(
        self, carousel_more_link_request: KakaoCarouselMoreLinkRequest, user: User, db: Session
    ):
        pass
