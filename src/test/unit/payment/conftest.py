import pytest

from src.auth.service.cafe24_service import Cafe24Service
from src.payment.service.cafe24_payment_service import Cafe24OrderService
from src.test.unit.auth.fixtures.mock_cafe24_repository import get_mock_cafe24_repository
from src.test.unit.auth.fixtures.mock_onboarding_repository import get_mock_onboarding_repository
from src.test.unit.payment.fixtures.mock_payment_repository import get_mock_payment_repository
from src.test.unit.users.fixtures.mock_user_repository import get_mock_user_repository
from src.users.service.user_service import UserService


@pytest.fixture
def mock_payment_repository():
    return get_mock_payment_repository()


@pytest.fixture
def mock_onboarding_repository():
    return get_mock_onboarding_repository()


@pytest.fixture
def mock_cafe24_repository():
    return get_mock_cafe24_repository()


@pytest.fixture
def mock_user_repository():
    return get_mock_user_repository()


@pytest.fixture
def user_service(mock_user_repository):
    return UserService(user_repository=mock_user_repository)


@pytest.fixture
def mock_cafe24_service(mock_user_repository, mock_cafe24_repository, mock_onboarding_repository):
    return Cafe24Service(
        user_repository=mock_user_repository,
        cafe24_repository=mock_cafe24_repository,
        onboarding_repository=mock_onboarding_repository,
    )


@pytest.fixture
def cafe24_order_service(mock_cafe24_service, mock_payment_repository):
    return Cafe24OrderService(
        payment_repository=mock_payment_repository, cafe24_service=mock_cafe24_service
    )
