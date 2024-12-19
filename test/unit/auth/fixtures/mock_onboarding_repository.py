from unittest.mock import MagicMock

from src.auth.service.port.base_onboarding_repository import BaseOnboardingRepository


def get_mock_onboarding_repository():
    mock_repository = MagicMock(spec_set=BaseOnboardingRepository)

    return mock_repository
