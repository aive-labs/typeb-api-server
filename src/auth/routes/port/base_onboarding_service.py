from abc import ABC, abstractmethod

from src.auth.enums.onboarding_status import OnboardingStatus
from src.auth.routes.dto.request.kakao_channel_request import KakaoChannelRequest
from src.auth.routes.dto.request.message_sender_request import MessageSenderRequest
from src.auth.routes.dto.response.onboarding_response import OnboardingResponse


class BaseOnboardingService(ABC):

    @abstractmethod
    def get_onboarding_status(self, mall_id: str) -> OnboardingResponse | None:
        pass

    @abstractmethod
    def update_onboarding_status(
        self, mall_id: str, status: OnboardingStatus
    ) -> OnboardingResponse:
        pass

    @abstractmethod
    def register_message_sender(self, mall_id: str, sender: MessageSenderRequest):
        pass

    # @abstractmethod
    # def get_message_sender(self, mall_id: str) -> MessageSenderResponse:
    #     pass

    @abstractmethod
    def register_kakao_channel(self, mall_id: str, kakao_channel: KakaoChannelRequest):
        pass

    # @abstractmethod
    # def get_kakao_channel(self, mall_id: str) -> KakaoChannelResponse:
    #     pass
