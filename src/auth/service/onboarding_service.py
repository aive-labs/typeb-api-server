from src.auth.enums.onboarding_status import OnboardingStatus
from src.auth.routes.dto.request.message_sender_request import MessageSenderRequest
from src.auth.routes.dto.response.message_sender_response import MessageSenderResponse
from src.auth.routes.dto.response.onboarding_response import OnboardingResponse
from src.auth.routes.port.base_onboarding_service import BaseOnboardingService
from src.auth.service.port.base_onboarding_repository import BaseOnboardingRepository


class OnboardingService(BaseOnboardingService):

    def __init__(self, onboarding_repository: BaseOnboardingRepository):
        self.onboarding_repository = onboarding_repository

    def register_message_sender(
        self, mall_id: str, message_sender: MessageSenderRequest
    ):
        self.onboarding_repository.save_message_sender(mall_id, message_sender)

    def get_message_sender(self, mall_id: str) -> MessageSenderResponse | None:
        return self.onboarding_repository.get_message_sender(mall_id)

    # def register_kakao_channel(self, mall_id: str, kakao_channel: KakaoChannelRequest):
    #
    # def get_kakao_channel(self, mall_id: str) -> KakaoChannelResponse:
    #     pass

    def get_onboarding_status(self, mall_id: str) -> OnboardingResponse | None:
        onboarding = self.onboarding_repository.get_onboarding_status(mall_id)

        if not onboarding:
            return None

        return OnboardingResponse(onboarding_status=onboarding.onboarding_status)

    def update_onboarding_status(
        self, mall_id: str, status: OnboardingStatus
    ) -> OnboardingResponse:
        onboarding = self.onboarding_repository.update_onboarding_status(
            mall_id, status
        )
        return OnboardingResponse(onboarding_status=onboarding.onboarding_status)
