from abc import ABC, abstractmethod

from fastapi import UploadFile
from sqlalchemy.orm import Session

from src.campaign.domain.vo.carousel_upload_link import CarouselUploadLinks
from src.messages.domain.kakao_carousel_card import KakaoCarouselCard
from src.users.domain.user import User


class UploadImageForMessageUseCase(ABC):

    @abstractmethod
    async def exec(
        self, campaign_id, set_group_msg_seq, files: list[UploadFile], user: User, db: Session
    ) -> dict:
        pass

    @abstractmethod
    async def upload_for_carousel(
        self, file: UploadFile, carousel_card: KakaoCarouselCard, user: User, db: Session
    ) -> CarouselUploadLinks:
        pass
