from datetime import datetime
from unittest.mock import MagicMock

import pytest
from dependency_injector import providers

from src.auth.utils.get_current_user import get_current_user
from src.auth.utils.permission_checker import get_permission_checker
from src.core.db_dependency import get_db
from src.core.exceptions.exceptions import NotFoundException
from src.main import app
from src.payment.enum.cafe24_payment_status import Cafe24PaymentStatus
from src.payment.routes.dto.response.cafe24_payment_response import (
    Cafe24PaymentResponse,
)
from src.payment.routes.use_case.get_cafe24_payment_usecase import (
    GetCafe24PaymentUseCase,
)


@pytest.fixture(autouse=True)
def override_dependencies(mock_user, mock_db, mock_cafe24_payment_service):
    app.dependency_overrides[get_current_user] = lambda: mock_user
    app.dependency_overrides[get_db] = lambda: mock_db

    def override_get_permission_checker(required_permissions=[]):
        return lambda: mock_user

    app.dependency_overrides[get_permission_checker] = override_get_permission_checker
    container = app.container
    container.cafe24_payment_service.override(providers.Object(mock_cafe24_payment_service))
    yield

    container.cafe24_payment_service.reset_override()
    app.dependency_overrides = {}


@pytest.fixture
def mock_cafe24_payment_service(mock_user, mock_db):
    service = MagicMock(spec=GetCafe24PaymentUseCase)

    # 동적으로 리턴값을 설정
    def exec(order_id, mock_user, mock_db):
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

    service.exec.side_effect = exec
    return service


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
