from src.auth.enums.onboarding_status import OnboardingStatus
from src.auth.routes.dto.request.kakao_channel_request import KakaoChannelRequest
from src.auth.routes.dto.request.message_sender_request import MessageSenderRequest
from src.auth.routes.dto.response.kakao_channel_response import KakaoChannelResponse
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
        # 카카오 채널 정보가 있는 경우, 카카오에 등록된 sender_phone_number랑 같아야함
        kakao_channel = self.onboarding_repository.get_kakao_channel(mall_id)
        if kakao_channel:
            if kakao_channel.sender_phone_number != message_sender.sender_phone_number:
                raise Exception(
                    "카카오 채널에 등록된 발신 번호와 등록하려는 발신 번호는 동일해야 합니다."
                )

        self.onboarding_repository.save_message_sender(mall_id, message_sender)

    def get_message_sender(self, mall_id: str) -> MessageSenderResponse | None:
        return self.onboarding_repository.get_message_sender(mall_id)

    def register_kakao_channel(self, mall_id: str, kakao_channel: KakaoChannelRequest):
        # 등록된 문자 발신자 정보가 있는 경우, 문자에 등록된 sender_phone_number랑 같아야함
        message_sender = self.onboarding_repository.get_message_sender(mall_id)
        if message_sender:
            if message_sender.sender_phone_number != kakao_channel.sender_phone_number:
                raise Exception(
                    "등록된 문자 발신번호와 카카오 채널 발신 번호는 동일해야 합니다."
                )
        self.onboarding_repository.save_kakao_channel(mall_id, kakao_channel)

    def get_kakao_channel(self, mall_id: str) -> KakaoChannelResponse | None:
        return self.onboarding_repository.get_kakao_channel(mall_id)

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
