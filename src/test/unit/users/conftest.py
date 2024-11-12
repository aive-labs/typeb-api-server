# test/users/conftest.py
import pytest

from src.test.unit.users.fixtures.create_token import create_access_token
from src.test.unit.users.fixtures.mock_user_repository import get_mock_user_repository
from src.users.service.user_service import UserService


@pytest.fixture
def mock_user_repository():
    return get_mock_user_repository()


@pytest.fixture
def user_service(mock_user_repository):
    return UserService(user_repository=mock_user_repository)


@pytest.fixture
def access_token():
    payload = {
        "email": "aivelabs",
        "department": "aivelabs",
        "mall_id": "aivelabs",
        "language": "ko",
        "permissions": "admin",
        "role": "admin",
        "subscription": {},
    }
    token = create_access_token(data=payload)
    return token
