from abc import ABC, abstractmethod

from sqlalchemy.orm import Session
from users.domain.user import User

from src.auth.enums.onboarding_status import OnboardingStatus
from src.auth.routes.dto.request.kakao_channel_request import KakaoChannelRequest
from src.auth.routes.dto.request.message_sender_request import MessageSenderRequest
from src.auth.routes.dto.response.kakao_channel_response import KakaoChannelResponse
from src.auth.routes.dto.response.message_sender_response import MessageSenderResponse
from src.auth.routes.dto.response.onboarding_response import OnboardingResponse
from src.core.transactional import transactional


class BaseOnboardingService(ABC):

    @abstractmethod
    @transactional
    def get_onboarding_status(
        self, mall_id: str, user: User, db: Session
    ) -> OnboardingResponse | None:
        pass

    @abstractmethod
    def update_onboarding_status(
        self, mall_id: str, status: OnboardingStatus, db: Session
    ) -> OnboardingResponse:
        pass

    @abstractmethod
    def register_message_sender(
        self, mall_id: str, message_sender: MessageSenderRequest, db: Session
    ):
        pass

    @abstractmethod
    def get_message_sender(
        self, mall_id: str, db: Session
    ) -> MessageSenderResponse | None:
        pass

    @abstractmethod
    def update_message_sender(
        self, mall_id: str, message_sender: MessageSenderRequest, db: Session
    ):
        pass

    @abstractmethod
    def register_kakao_channel(
        self, mall_id: str, kakao_channel: KakaoChannelRequest, db: Session
    ):
        pass

    @abstractmethod
    def update_kakao_channel(
        self, mall_id: str, kakao_channel: KakaoChannelRequest, db: Session
    ):
        pass

    @abstractmethod
    def get_kakao_channel(
        self, mall_id: str, db: Session
    ) -> KakaoChannelResponse | None:
        pass
