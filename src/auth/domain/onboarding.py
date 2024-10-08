from datetime import datetime

from pydantic import BaseModel

from src.auth.enums.onboarding_status import OnboardingStatus


class Onboarding(BaseModel):
    mall_id: str
    onboarding_status: OnboardingStatus
    created_at: datetime
    updated_at: datetime
