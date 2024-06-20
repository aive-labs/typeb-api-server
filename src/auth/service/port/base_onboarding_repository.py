from abc import ABC, abstractmethod

from src.auth.domain.onboarding import Onboarding


class BaseOnboardingRepository(ABC):

    @abstractmethod
    def get_onboarding_status(self, mall_id) -> Onboarding | None:
        pass

    @abstractmethod
    def update_onboarding_status(self, mall_id, status) -> Onboarding:
        pass

    @abstractmethod
    def insert_first_onboarding(self, mall_id: str):
        pass
