from enum import Enum


class OnboardingStatus(Enum):
    CAFE24_INTEGRATION_REQUIRED = "cafe24_integration_required"
    MIGRATION_IN_PROGRESS = "migration_in_progress"
    MIGRATION_COMPLETED = "migration_completed"
    SENDER_INFO_REQUIRED = "sender_info_required"
    ONBOARDING_COMPLETE = "onboarding_complete"
