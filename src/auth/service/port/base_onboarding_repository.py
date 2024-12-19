from abc import ABC, abstractmethod

from sqlalchemy.orm import Session

from src.auth.domain.onboarding import Onboarding
from src.auth.model.response.kakao_channel_response import KakaoChannelResponse
from src.auth.model.response.message_sender_response import MessageSenderResponse
from src.user.domain.user import User


class BaseOnboardingRepository(ABC):

    @abstractmethod
    def get_onboarding_status(self, mall_id, db: Session) -> Onboarding | None:
        pass

    @abstractmethod
    def update_onboarding_status(self, mall_id, status, db: Session) -> Onboarding:
        pass

    @abstractmethod
    def insert_first_onboarding(self, mall_id: str, db: Session):
        pass

    @abstractmethod
    def save_message_sender(self, mall_id, message_sender, db: Session):
        pass

    @abstractmethod
    def update_message_sender(self, mall_id, message_sender, db):
        pass

    @abstractmethod
    def get_message_sender(self, mall_id, db: Session) -> MessageSenderResponse | None:
        pass

    @abstractmethod
    def save_kakao_channel(self, mall_id, kakao_channel, db: Session):
        pass

    @abstractmethod
    def update_kakao_channel(self, mall_id, kakao_channel, db: Session):
        pass

    @abstractmethod
    def get_kakao_channel(self, mall_id, db: Session) -> KakaoChannelResponse | None:
        pass

    @abstractmethod
    def get_kakao_sender_key(self, mall_id, db: Session) -> str | None:
        pass

    @abstractmethod
    def get_opt_out_phone_number(self, user: User, db: Session) -> str | None:
        pass
