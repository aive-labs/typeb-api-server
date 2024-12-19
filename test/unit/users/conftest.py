# test/user/conftest.py
import pytest

from src.user.service.user_service import UserService
from test.unit.users.fixtures.mock_user_repository import get_mock_user_repository


@pytest.fixture
def mock_user_repository():
    return get_mock_user_repository()


@pytest.fixture
def user_service(mock_user_repository):
    return UserService(user_repository=mock_user_repository)
