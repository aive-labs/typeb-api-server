from pydantic import BaseModel

from src.auth.model.onboarding_status import OnboardingStatus


class OnboardingResponse(BaseModel):
    onboarding_status: OnboardingStatus
