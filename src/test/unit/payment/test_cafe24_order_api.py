from unittest.mock import MagicMock

import pytest
from dependency_injector import providers
from src.auth.utils.get_current_user import get_current_user
from src.auth.utils.permission_checker import get_permission_checker
from src.core.db_dependency import get_db
from src.main import app
from src.payment.routes.dto.request.cafe24_order_request import Cafe24OrderRequest
from src.payment.routes.dto.response.cafe24_order_response import Cafe24OrderResponse
from src.payment.routes.use_case.create_cafe24_order_usecase import CreateCafe24OrderUseCase


@pytest.fixture(autouse=True)
def override_dependencies(mock_user, mock_db, mock_cafe24_order_service):
    app.dependency_overrides[get_current_user] = lambda: mock_user
    app.dependency_overrides[get_db] = lambda: mock_db

    def override_get_permission_checker(required_permissions=[]):
        return lambda: mock_user

    app.dependency_overrides[get_permission_checker] = override_get_permission_checker
    container = app.container
    container.cafe24_order_service.override(providers.Object(mock_cafe24_order_service))

    yield
    container.cafe24_order_service.reset_override()
    app.dependency_overrides = {}


@pytest.fixture
def mock_cafe24_order_service():
    service = MagicMock(spec=CreateCafe24OrderUseCase)

    def exec(mock_user, mock_db, cafe24_order_request: Cafe24OrderRequest):
        order_response = Cafe24OrderResponse(
            order_id=cafe24_order_request.order_id,
            cafe24_order_id="cafe24-20180704-100000000",
            confirmation_url="https://sample_shop.cafe24.com",
            return_url="https://aace.ai/billing/cafe24-order-result",
            order_amount=cafe24_order_request.order_amount,
        )
        return order_response

    service.exec.side_effect = exec
    return service


def test__카페24_주문_생성_요청__성공시_응답코드_200과_데이터를_응답한다(
    test_client,
    access_token,
):
    headers = {"Authorization": f"Bearer {access_token}"}

    body = {
        "order_name": "order1",
        "order_amount": 30000,
    }

    response = test_client.post("api/v1/payment/cafe24-order", headers=headers, json=body)
    assert response.status_code == 200

    data = response.json()
    assert data["order_id"] is not None
    assert data["cafe24_order_id"] is not None
    assert "billing/cafe24-order-result" in data["return_url"]
    assert data["confirmation_url"] is not None
    assert data["order_amount"] == float(body["order_amount"])


def test__카페24_주문_생성_요청__필드명을_잘못_입력하면_422를_응답한다(
    test_client,
    access_token,
):
    headers = {"Authorization": f"Bearer {access_token}"}

    body = {
        "name": "order1",
        "amount": 30000,
    }

    response = test_client.post("api/v1/payment/cafe24-order", headers=headers, json=body)
    assert response.status_code == 422


@pytest.mark.parametrize(
    "body, expected_status_code, expected_detail",
    [
        # order_name 누락
        (
            {"order_amount": "order_name"},
            422,
            "invalid type",
        ),
        # order_amount 누락
        (
            {"order_name": "order1"},
            422,
            "field required",
        ),
        # order_name 타입 오류 (정수형 입력)
        (
            {"order_name": 12345, "order_amount": 30000},
            422,
            "str type expected",
        ),
        # order_amount 타입 오류 (문자열 입력)
        (
            {"order_name": "order1", "order_amount": "삼만 원"},
            422,
            "value is not a valid float",
        ),
        # 잘못된 필드명 사용 (order_name을 order_nam으로 오타)
        (
            {"order_nam": "order1", "order_amount": 30000},
            422,
            "field required",
        ),
        # 잘못된 필드명 사용 (order_amount를 order_amunt로 오타)
        (
            {"order_name": "order1", "order_amunt": 30000},
            422,
            "field required",
        ),
        # 추가적인 유효성 검사 (order_amount가 음수)
        (
            {"order_name": "order1", "order_amount": -1000},
            422,
            "ensure this value is greater than 0",
        ),
        # 추가적인 유효성 검사 (order_name이 빈 문자열)
        (
            {"order_name": "", "order_amount": 30000},
            422,
            "ensure this value has at least 1 characters",
        ),
    ],
)
def test__카페24_주문_생성_요청__유효성_검사(
    test_client, access_token, body, expected_status_code, expected_detail
):
    headers = {"Authorization": f"Bearer {access_token}"}

    response = test_client.post("api/v1/payment/cafe24-order", headers=headers, json=body)
    assert response.status_code == expected_status_code
