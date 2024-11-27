from datetime import datetime
from unittest.mock import AsyncMock, MagicMock

import pytest

from src.auth.service.cafe24_service import Cafe24Service
from src.common.utils.get_env_variable import get_env_variable
from src.core.exceptions.exceptions import Cafe24Exception, NotFoundException
from src.payment.domain.cafe24_order import Cafe24Order
from src.payment.domain.cafe24_payment import Cafe24Payment
from src.payment.enum.cafe24_payment_status import Cafe24PaymentStatus
from src.payment.routes.dto.request.cafe24_order_request import Cafe24OrderRequest
from src.payment.service.cafe24_order_service import Cafe24OrderService
from src.payment.service.get_cafe24_payment_service import GetCafe24PaymentService
from src.test.unit.auth.fixtures.mock_cafe24_repository import get_mock_cafe24_repository
from src.test.unit.auth.fixtures.mock_onboarding_repository import get_mock_onboarding_repository
from src.test.unit.payment.fixtures.mock_payment_repository import get_mock_payment_repository
from src.test.unit.payment.fixtures.mock_subscription_repository import (
    get_mock_subscription_repository,
)
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


@pytest.fixture()
def mock_subscription_repository():
    return get_mock_subscription_repository()


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
            return_url=f"{get_env_variable('order_return_url')}",
            confirmation_url="https://samplemall.cafe24.com/disp/common/myapps/order?signature=BAhpBBMxojw%3D--d1c0134218f0ff3c0f57cb3b57bcc34e6f170727",
            automatic_payment="F",
            currency="KRW",
        )

    def get_payment(order_id, user):
        if order_id == "cafe24-20180704-100000000":
            return Cafe24Payment(
                order_id=order_id,
                payment_status=Cafe24PaymentStatus.PAID,
                title="테스트 주문",
                approval_no="",
                payment_gateway_name="",
                payment_method="card",
                payment_amount=1000.00,
                refund_amount=None,
                currency="KRW",
                locale_code="KO",
                automatic_payment="F",
                pay_date=datetime.now(),
                refund_date=datetime.now(),
                expiration_date=datetime.now(),
            )
        else:
            raise Cafe24Exception(
                detail={"message": "주문 정보와 일치하는 결제정보를 찾지 못했습니다."}
            )

    service.create_order = AsyncMock(side_effect=create_order)
    service.get_payment = AsyncMock(side_effect=get_payment)

    return service


@pytest.fixture
def cafe24_order_service(mock_cafe24_service, mock_payment_repository):
    return Cafe24OrderService(
        payment_repository=mock_payment_repository, cafe24_service=mock_cafe24_service
    )


@pytest.fixture
def cafe24_payment_service(
    mock_cafe24_service, mock_payment_repository, mock_subscription_repository
):
    return GetCafe24PaymentService(
        payment_repository=mock_payment_repository,
        cafe24_service=mock_cafe24_service,
        subscription_repository=mock_subscription_repository,
    )
