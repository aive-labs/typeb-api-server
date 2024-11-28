import pytest

from src.users.domain.user import User


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


def test__사용자는_상품_상세_조회를_할_수_있다(product_service, mock_db, default_user):
    product_id = 1
    product = product_service.get_product_detail(f"P{product_id}", mock_db)

    assert product.name == "상품명 1"
    assert product.category_1 == "카테고리1_1"
    assert product.recommend_yn == "Y" if product_id % 2 == 0 else "N"
    assert product.sale_yn == "Y"
    assert product.price == 10000 + product_id * 1000
    assert product.discount_price == 9000 + product_id * 900
