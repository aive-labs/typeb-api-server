from abc import ABC, abstractmethod

from sqlalchemy.orm import Session

from src.main.transactional import transactional
from src.message.model.request.kakao_carousel_more_link_request import (
    KakaoCarouselMoreLinkRequest,
)
from src.user.domain.user import User


class CreateCarouselMoreLinkUseCase(ABC):

    @transactional
    @abstractmethod
    def exec(
        self,
        set_group_msg_seq: int,
        carousel_more_link_request: KakaoCarouselMoreLinkRequest,
        user: User,
        db: Session,
    ):
        pass
