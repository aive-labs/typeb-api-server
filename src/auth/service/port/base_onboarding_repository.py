from abc import ABC, abstractmethod

from src.auth.domain.onboarding import Onboarding


class BaseOnboardingRepository(ABC):

    @abstractmethod
    def get_onboarding_status(self, mall_id) -> Onboarding:
        pass

    @abstractmethod
    def update_onboarding_status(self, mall_id, status) -> Onboarding:
        pass
