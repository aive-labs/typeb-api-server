from unittest.mock import AsyncMock

import pytest

from src.auth.service.cafe24_service import Cafe24Service
from src.common.utils.get_env_variable import get_env_variable
from src.payment.domain.cafe24_order import Cafe24Order
from src.payment.routes.dto.request.cafe24_order_request import Cafe24OrderRequest
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
    service = Cafe24Service(
        user_repository=mock_user_repository,
        cafe24_repository=mock_cafe24_repository,
        onboarding_repository=mock_onboarding_repository,
    )

    def create_order(user, order_request: Cafe24OrderRequest):
        return Cafe24Order(
            order_id="order123",
            cafe24_order_id="cafe24-20180704-100000000",
            order_name=order_request.order_name,
            order_amount=order_request.order_amount,
            return_url=f"{get_env_variable('order_return_url')}?cafe24_order_id=cafe24-20180704-100000000",
            confirmation_url="https://samplemall.cafe24.com/disp/common/myapps/order?signature=BAhpBBMxojw%3D--d1c0134218f0ff3c0f57cb3b57bcc34e6f170727",
            automatic_payment="F",
            currency="KRW",
        )

    service.create_order = AsyncMock(side_effect=create_order)
    return service


@pytest.fixture
def cafe24_order_service(mock_cafe24_service, mock_payment_repository):
    return Cafe24OrderService(
        payment_repository=mock_payment_repository, cafe24_service=mock_cafe24_service
    )
