from sqlalchemy.orm import Session

from src.auth.domain.onboarding import Onboarding
from src.auth.enums.onboarding_status import OnboardingStatus
from src.auth.infra.onboarding_sqlalchemy_repository import (
    OnboardingSqlAlchemyRepository,
)
from src.auth.routes.dto.response.kakao_channel_response import KakaoChannelResponse
from src.auth.routes.dto.response.message_sender_response import MessageSenderResponse
from src.auth.service.port.base_onboarding_repository import BaseOnboardingRepository
from src.user.domain.user import User


class OnboardingRepository(BaseOnboardingRepository):

    def __init__(self, onboarding_sqlalchemy: OnboardingSqlAlchemyRepository):
        self.onboarding_sqlalchemy = onboarding_sqlalchemy

    def get_onboarding_status(self, mall_id, db: Session) -> Onboarding | None:
        return self.onboarding_sqlalchemy.get_onboarding_status(mall_id, db)

    def update_onboarding_status(
        self, mall_id: str, status: OnboardingStatus, db: Session
    ) -> Onboarding:
        return self.onboarding_sqlalchemy.update_onboarding_status(mall_id, status, db)

    def insert_first_onboarding(self, mall_id: str, db: Session):
        self.onboarding_sqlalchemy.insert_first_onboarding(mall_id, db)

    def save_message_sender(self, mall_id, message_sender, db: Session):
        self.onboarding_sqlalchemy.save_message_sender(mall_id, message_sender, db)

    def get_message_sender(self, mall_id, db: Session) -> MessageSenderResponse | None:
        return self.onboarding_sqlalchemy.get_message_sender(mall_id, db)

    def update_message_sender(self, mall_id, message_sender, db):
        return self.onboarding_sqlalchemy.update_message_sender(mall_id, message_sender, db)

    def save_kakao_channel(self, mall_id, kakao_channel, db: Session):
        self.onboarding_sqlalchemy.save_kakao_channel(mall_id, kakao_channel, db)

    def update_kakao_channel(self, mall_id, kakao_channel, db: Session):
        self.onboarding_sqlalchemy.update_kakao_channel(mall_id, kakao_channel, db)

    def get_kakao_channel(self, mall_id, db: Session) -> KakaoChannelResponse | None:
        return self.onboarding_sqlalchemy.get_kakao_channel(mall_id, db)

    def get_kakao_sender_key(self, mall_id, db: Session) -> str | None:
        return self.onboarding_sqlalchemy.get_kakao_sender_key(mall_id, db)

    def get_opt_out_phone_number(self, user: User, db: Session) -> str | None:
        return self.onboarding_sqlalchemy.get_opt_out_phone_number(user, db)
