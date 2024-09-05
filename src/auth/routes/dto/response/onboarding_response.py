from pydantic import BaseModel

from src.auth.enums.onboarding_status import OnboardingStatus


class OnboardingResponse(BaseModel):
    onboarding_status: OnboardingStatus
