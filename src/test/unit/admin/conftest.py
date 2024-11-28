import pytest

from src.admin.service.personal_information_service import PersonalInformationService
from src.test.unit.admin.fixtures.mock_personal_information_repository import (
    get_mock_personal_information_repository,
)


@pytest.fixture
def mock_personal_information_repository():
    return get_mock_personal_information_repository()


@pytest.fixture
def personal_information_service(mock_personal_information_repository):
    return PersonalInformationService(
        personal_information_repository=mock_personal_information_repository
    )
