import pytest
from fastapi import HTTPException

from src.common.utils.get_env_variable import get_env_variable
from src.core.exceptions.exceptions import ConsistencyException
from src.payment.routes.dto.request.cafe24_order_request import Cafe24OrderRequest
from src.payment.routes.dto.response.cafe24_order_response import Cafe24OrderResponse
from src.user.domain.user import User


@pytest.fixture
def default_user():
    return User(
        user_id=1,
        username="테스트",
        password="테스트",
        email="test@test.com",
        role_id="admin",
        photo_uri="",
        department_id="1",
        brand_name_ko="브랜드",
        brand_name_en="brand",
        language="ko",
        cell_phone_number="010-1234-1234",
        test_callback_number="010-1234-1234",
        mall_id="aivelabs",
    )


@pytest.mark.asyncio
async def test__cafe24_주문_요청__사용자의_쇼핑몰_정보가_없으면_예외를_던진다(
    cafe24_order_service, mock_db, default_user
):
    cafe24_order_request = Cafe24OrderRequest(order_name="테스트 주문", order_amount=10000)
    default_user.mall_id = None

    with pytest.raises(HTTPException) as exc_info:
        await cafe24_order_service.exec(
            user=default_user, db=mock_db, order_request=cafe24_order_request
        )

    assert exc_info.type == ConsistencyException
    assert (
        str(exc_info.value.detail["message"])  # pyright: ignore [reportArgumentType]
        == "등록된 쇼핑몰 정보가 없습니다."
    )


@pytest.mark.asyncio
async def test__cafe24_주문_요청__주문_정보를_생성한다(cafe24_order_service, mock_db, default_user):
    cafe24_order_request = Cafe24OrderRequest(order_name="테스트 주문", order_amount=20000)

    response = await cafe24_order_service.exec(default_user, mock_db, cafe24_order_request)
    print(response)

    assert isinstance(response, Cafe24OrderResponse)
    assert response.order_id is not None
    assert response.cafe24_order_id is not None
    assert response.return_url is not None

    base_return_url = get_env_variable("order_return_url")
    assert response.return_url == base_return_url

    assert response.confirmation_url is not None

    assert response.order_amount == float(cafe24_order_request.order_amount)

    cafe24_order_service.cafe24_service.create_order.assert_called_once_with(
        default_user, cafe24_order_request
    )
    cafe24_order_service.payment_repository.save_cafe24_order.assert_called_once()
