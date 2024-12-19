from abc import ABC, abstractmethod

from sqlalchemy.orm import Session

from src.auth.model.onboarding_status import OnboardingStatus
from src.auth.model.request.kakao_channel_request import KakaoChannelRequest
from src.auth.model.request.message_sender_request import MessageSenderRequest
from src.auth.model.response.kakao_channel_response import KakaoChannelResponse
from src.auth.model.response.message_sender_response import MessageSenderResponse
from src.auth.model.response.onboarding_response import OnboardingResponse
from src.main.transactional import transactional
from src.message_template.model.response.opt_out_phone_number_response import (
    OptOutPhoneNumberResponse,
)
from src.user.domain.user import User


class BaseOnboardingService(ABC):

    @transactional
    @abstractmethod
    def get_onboarding_status(
        self, mall_id: str, user: User, db: Session
    ) -> OnboardingResponse | None:
        pass

    @transactional
    @abstractmethod
    def update_onboarding_status(
        self, mall_id: str, status: OnboardingStatus, db: Session
    ) -> OnboardingResponse:
        pass

    @transactional
    @abstractmethod
    def register_message_sender(
        self, mall_id: str, message_sender: MessageSenderRequest, db: Session
    ):
        pass

    @transactional
    @abstractmethod
    def get_message_sender(self, mall_id: str, db: Session) -> MessageSenderResponse | None:
        pass

    @transactional
    @abstractmethod
    def update_message_sender(
        self, mall_id: str, message_sender: MessageSenderRequest, db: Session
    ):
        pass

    @transactional
    @abstractmethod
    def register_kakao_channel(self, mall_id: str, kakao_channel: KakaoChannelRequest, db: Session):
        pass

    @transactional
    @abstractmethod
    def update_kakao_channel(self, mall_id: str, kakao_channel: KakaoChannelRequest, db: Session):
        pass

    @transactional
    @abstractmethod
    def get_kakao_channel(self, mall_id: str, db: Session) -> KakaoChannelResponse | None:
        pass

    @abstractmethod
    def get_opt_out_phone_number(self, user: User, db: Session) -> OptOutPhoneNumberResponse:
        pass
