from abc import ABC, abstractmethod

from sqlalchemy.orm import Session

from src.auth.domain.onboarding import Onboarding
from src.auth.routes.dto.response.kakao_channel_response import KakaoChannelResponse
from src.auth.routes.dto.response.message_sender_response import MessageSenderResponse


class BaseOnboardingRepository(ABC):

    @abstractmethod
    def get_onboarding_status(self, mall_id, db: Session) -> Onboarding | None:
        pass

    @abstractmethod
    def update_onboarding_status(self, mall_id, status) -> Onboarding:
        pass

    @abstractmethod
    def insert_first_onboarding(self, mall_id: str):
        pass

    @abstractmethod
    def save_message_sender(self, mall_id, message_sender):
        pass

    @abstractmethod
    def get_message_sender(self, mall_id) -> MessageSenderResponse | None:
        pass

    @abstractmethod
    def save_kakao_channel(self, mall_id, kakao_channel):
        pass

    @abstractmethod
    def get_kakao_channel(self, mall_id) -> KakaoChannelResponse | None:
        pass
