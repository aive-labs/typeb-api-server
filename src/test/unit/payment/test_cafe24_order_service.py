import pytest
from fastapi import HTTPException

from src.core.exceptions.exceptions import ConsistencyException
from src.payment.routes.dto.request.cafe24_order_request import Cafe24OrderRequest
from src.users.domain.user import User
from src.users.routes.dto.request.user_create import UserCreate


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
    )


@pytest.mark.asyncio
async def test__cafe24_주문_요청__쇼핑몰_정보가_없으면_예외를_던진다(
    cafe24_order_service, mock_db, default_user
):
    cafe24_order_request = Cafe24OrderRequest(order_name="테스트 주문", order_amount=10000)

    with pytest.raises(HTTPException) as exc_info:
        await cafe24_order_service.exec(
            user=default_user, db=mock_db, order_request=cafe24_order_request
        )

    assert exc_info.type == ConsistencyException
    assert (
        str(exc_info.value.detail["message"])
        == "등록된 쇼핑몰 정보가 없습니다."  # pyright: ignore [reportArgumentType]
    )
