import pytest
from fastapi import HTTPException

from src.core.exceptions.exceptions import NotFoundException
from src.payment.enum.cafe24_payment_status import Cafe24PaymentStatus
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
async def test__cafe24_결제_조회_요청__결제_정보가_없으면_예외를_던진다(
    cafe24_payment_service, mock_db, default_user
):
    not_matched_order_id = "cafe24-20180704-585654234234"

    with pytest.raises(HTTPException) as exc_info:
        await cafe24_payment_service.exec(not_matched_order_id, default_user, mock_db)

    assert exc_info.type == NotFoundException
    assert (
        str(exc_info.value.detail["message"])  # pyright: ignore [reportArgumentType]
        == "주문 및 결제 정보를 찾지 못했습니다."
    )

    cafe24_payment_service.cafe24_service.get_payment.assert_not_called()
    cafe24_payment_service.payment_repository.save_cafe24_payment.assert_not_called()


@pytest.mark.asyncio
async def test__cafe24_결제_조회_요청__결제_정보를_응답한다(
    cafe24_payment_service, mock_db, default_user
):
    matched_order_id = "cafe24-20180704-100000000"

    response = await cafe24_payment_service.exec(matched_order_id, default_user, mock_db)

    assert response.cafe24_order_id == matched_order_id
    assert response.payment_status == Cafe24PaymentStatus.PAID

    cafe24_payment_service.payment_repository.save_cafe24_payment.assert_called_once()
