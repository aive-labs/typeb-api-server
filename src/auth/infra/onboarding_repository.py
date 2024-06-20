from src.auth.domain.onboarding import Onboarding
from src.auth.enums.onboarding_status import OnboardingStatus
from src.auth.infra.onboarding_sqlalchemy_repository import (
    OnboardingSqlAlchemyRepository,
)
from src.auth.service.port.base_onboarding_repository import BaseOnboardingRepository


class OnboardingRepository(BaseOnboardingRepository):

    def __init__(self, onboarding_sqlalchemy: OnboardingSqlAlchemyRepository):
        self.onboarding_sqlalchemy = onboarding_sqlalchemy

    def get_onboarding_status(self, mall_id) -> Onboarding | None:
        return self.onboarding_sqlalchemy.get_onboarding_status(mall_id)

    def update_onboarding_status(
        self, mall_id: str, status: OnboardingStatus
    ) -> Onboarding:
        return self.onboarding_sqlalchemy.update_onboarding_status(mall_id, status)

    def insert_first_onboarding(self, mall_id: str):
        self.onboarding_sqlalchemy.insert_first_onboarding(mall_id)
