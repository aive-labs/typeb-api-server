from pydantic import BaseModel

from src.auth.enums.onboarding_status import OnboardingStatus


class OnboardingRequest(BaseModel):
    onboarding_status: OnboardingStatus
