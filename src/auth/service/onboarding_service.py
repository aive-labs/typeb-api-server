from src.auth.enums.onboarding_status import OnboardingStatus
from src.auth.routes.dto.request.kakao_channel_request import KakaoChannelRequest
from src.auth.routes.dto.request.message_sender_request import MessageSenderRequest
from src.auth.routes.dto.response.kakao_channel_response import KakaoChannelResponse
from src.auth.routes.dto.response.message_sender_response import MessageSenderResponse
from src.auth.routes.dto.response.onboarding_response import OnboardingResponse
from src.auth.routes.port.base_onboarding_service import BaseOnboardingService
from src.auth.service.port.base_onboarding_repository import BaseOnboardingRepository


class OnboardingService(BaseOnboardingService):

    def __int__(self, onboarding_repository: BaseOnboardingRepository):
        self.onboarding_repository = onboarding_repository

    def register_message_sender(self, mall_id: str, sender: MessageSenderRequest):
        pass

    def get_message_sender(self, mall_id: str) -> MessageSenderResponse:
        pass

    def register_kakao_channel(self, mall_id: str, kakao_channel: KakaoChannelRequest):
        pass

    def get_kakao_channel(self, mall_id: str) -> KakaoChannelResponse:
        pass

    def get_onboarding_status(self, mall_id: str) -> OnboardingResponse:
        onboarding = self.onboarding_repository.get_onboarding_status(mall_id)
        return OnboardingResponse(onboarding_status=onboarding.onboarding_status)

    def update_onboarding_status(
        self, mall_id: str, status: OnboardingStatus
    ) -> OnboardingResponse:
        onboarding = self.onboarding_repository.update_onboarding_status(
            mall_id, status
        )
        return OnboardingResponse(onboarding_status=onboarding.onboarding_status)
