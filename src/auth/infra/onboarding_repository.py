from sqlalchemy import text
from sqlalchemy.orm import Session

from src.auth.domain.onboarding import Onboarding
from src.auth.enums.onboarding_status import OnboardingStatus
from src.auth.infra.onboarding_sqlalchemy_repository import (
    OnboardingSqlAlchemyRepository,
)
from src.auth.routes.dto.response.kakao_channel_response import KakaoChannelResponse
from src.auth.routes.dto.response.message_sender_response import MessageSenderResponse
from src.auth.service.port.base_onboarding_repository import BaseOnboardingRepository


class OnboardingRepository(BaseOnboardingRepository):

    def __init__(self, onboarding_sqlalchemy: OnboardingSqlAlchemyRepository):
        self.onboarding_sqlalchemy = onboarding_sqlalchemy

    def get_onboarding_status(self, mall_id, db: Session) -> Onboarding | None:
        print(f"repository_db_session: {db}")
        result = db.execute(text("SHOW search_path")).fetchone()
        print(f"Current search_path: {result}")

        return self.onboarding_sqlalchemy.get_onboarding_status(mall_id, db)

    def update_onboarding_status(
        self, mall_id: str, status: OnboardingStatus
    ) -> Onboarding:
        return self.onboarding_sqlalchemy.update_onboarding_status(mall_id, status)

    def insert_first_onboarding(self, mall_id: str):
        self.onboarding_sqlalchemy.insert_first_onboarding(mall_id)

    def save_message_sender(self, mall_id, message_sender):
        self.onboarding_sqlalchemy.save_message_sender(mall_id, message_sender)

    def get_message_sender(self, mall_id) -> MessageSenderResponse | None:
        return self.onboarding_sqlalchemy.get_message_sender(mall_id)

    def save_kakao_channel(self, mall_id, kakao_channel):
        self.onboarding_sqlalchemy.save_kakao_channel(mall_id, kakao_channel)

    def get_kakao_channel(self, mall_id) -> KakaoChannelResponse | None:
        return self.onboarding_sqlalchemy.get_kakao_channel(mall_id)
