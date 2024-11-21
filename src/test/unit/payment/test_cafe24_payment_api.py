from datetime import datetime
from unittest.mock import MagicMock

import pytest
from dependency_injector import providers
from starlette.testclient import TestClient

from src.auth.routes.port.base_oauth_service import BaseOauthService
from src.auth.utils.get_current_user import get_current_user
from src.auth.utils.permission_checker import get_permission_checker
from src.core.db_dependency import get_db
from src.core.exceptions.exceptions import NotFoundException
from src.main import app
from src.payment.domain.cafe24_order import Cafe24Order
from src.payment.domain.cafe24_payment import Cafe24Payment
from src.payment.enum.cafe24_payment_status import Cafe24PaymentStatus
from src.payment.enum.payment_status import PaymentStatus
from src.payment.routes.dto.response.cafe24_order_response import Cafe24OrderResponse
from src.payment.routes.dto.response.cafe24_payment_response import Cafe24PaymentResponse
from src.payment.routes.use_case.create_cafe24_order_usecase import CreateCafe24OrderUseCase
from src.payment.routes.use_case.get_cafe24_payment_usecase import GetCafe24PaymentUseCase
from src.users.domain.user import User


@pytest.fixture
def test_client():
    with TestClient(app) as client:
        yield client


@pytest.fixture
def test_cafe24_payment_response():
    return {
        "payments": [
            {
                "order_id": "cafe24-20180704-100000000",
                "payment_status": "paid",
                "title": "App Name_App Store Order1",
                "approval_no": "10000000",
                "payment_gateway_name": "allat",
                "payment_method": "card",
                "payment_amount": "1000.00",
                "refund_amount": "0.00",
                "currency": "KRW",
                "locale_code": "ko_KR",
                "automatic_payment": "T",
                "pay_date": "2018-07-04T11:19:27+09:00",
                "refund_date": None,
                "expiration_date": "2018-08-04T11:19:27+09:00",
            }
        ]
    }


@pytest.fixture
def mock_cafe24_order_service():
    service = MagicMock(spec=CreateCafe24OrderUseCase)

    sample_order_id = "9f4eabfd-159a-4968-827f-3234235b9eba"

    order_response = Cafe24OrderResponse(
        order_id=sample_order_id,
        cafe24_order_id="cafe24-20180704-100000000",
        confirmation_url="https://sample_shop.cafe24.com",
        return_url="https://aace.ai/billing/cafe24-order-result?signature=BAhpBBMxojw%3D--d1c0134218f0ff3c0f57cb3b57bcc34e6f170727",
    )

    service.exec.return_value = order_response
    return service


@pytest.fixture
def mock_cafe24_payment_service(mock_user, mock_db):
    service = MagicMock(spec=GetCafe24PaymentUseCase)

    # 동적으로 리턴값을 설정
    def dynamic_response(order_id, mock_user, mock_db):
        if order_id == "cafe24-20180704-100000000":
            return Cafe24PaymentResponse(
                cafe24_order_id=order_id,
                payment_status=Cafe24PaymentStatus.PAID,
                title="payment_title",
                payment_amount=1000.00,
                refund_amount=None,
                payment_method="card",
                currency="KRW",
                pay_date=datetime.now(),
            )
        else:
            # 존재하지 않는 주문 ID에 대해 예외를 발생시키거나 None 반환
            raise NotFoundException(detail={"message": "주문 및 결제 정보를 찾지 못했습니다."})

    service.exec.side_effect = dynamic_response
    return service


@pytest.fixture(autouse=True)
def override_dependencies(
    mock_user, mock_db, mock_cafe24_order_service, mock_cafe24_payment_service
):
    # get_current_user 의존성 오버라이드
    app.dependency_overrides[get_current_user] = lambda: mock_user

    # get_db 의존성 오버라이드
    app.dependency_overrides[get_db] = lambda: mock_db

    # get_permission_checker 의존성 오버라이드
    def override_get_permission_checker(required_permissions=[]):
        return lambda: mock_user

    app.dependency_overrides[get_permission_checker] = override_get_permission_checker

    container = app.container

    # 프로바이더 오버라이드 설정
    container.cafe24_order_service.override(providers.Object(mock_cafe24_order_service))
    container.cafe24_payment_service.override(providers.Object(mock_cafe24_payment_service))

    yield

    # 테스트 후 오버라이드 리셋
    container.cafe24_order_service.reset_override()
    container.cafe24_payment_service.reset_override()
    app.dependency_overrides = {}


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
    assert data["order_id"] == "9f4eabfd-159a-4968-827f-3234235b9eba"
    assert data["cafe24_order_id"] is not None
    assert "billing/cafe24-order-result" in data["return_url"]
    assert data["confirmation_url"] is not None


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


def test__카페24_결제_확인_요청__성공하면_데이터와_응답코드_200을_응답한다(
    test_client,
    access_token,
):
    headers = {"Authorization": f"Bearer {access_token}"}

    query_params = {"cafe24_order_id": "cafe24-20180704-100000000"}
    response = test_client.get(
        "api/v1/payment/cafe24-payment", headers=headers, params=query_params
    )
    assert response.status_code == 200


def test__카페24_결제_확인_요청__해당하는_order_id가_없으면_404를_응답한다(
    test_client, access_token
):
    headers = {"Authorization": f"Bearer {access_token}"}

    query_params = {"cafe24_order_id": "1231221312"}
    response = test_client.get(
        "api/v1/payment/cafe24-payment", headers=headers, params=query_params
    )

    assert response.status_code == 404
    assert response.json()["detail"]["message"] == "주문 및 결제 정보를 찾지 못했습니다."
