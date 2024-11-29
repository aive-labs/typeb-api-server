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


def test__사용자는_상품_전체를_조회할_수_있다(product_service, mock_db, default_user):
    all_products = product_service.get_all_products(
        based_on="product_code", sort_by="desc", current_page=1, per_page=20, db=mock_db
    )

    # 전체 상품 수 확인
    assert len(all_products) == 10

    # 정렬 확인
    product_nos = [product.id for product in all_products]
    assert product_nos == sorted(
        product_nos, reverse=True
    ), "Product_no 기준으로 내림차순 정렬이 되어야 한다."


@pytest.mark.parametrize(
    # 전체 데이터는 20개 가정
    "current_page, per_page, expected_count, sort_by",
    [
        (1, 5, 5, "asc"),  # 첫 번째 페이지, 5개씩, 5개 조회 예상
        (2, 5, 5, "asc"),  # 두 번째 페이지, 5개씩, 5개 조회 예상
        (3, 5, 5, "desc"),  # 세 번째 페이지, 5개씩, 5개 조회 예상
        (4, 5, 5, "desc"),  # 네 번째 페이지, 5개씩, 5개 조회 예상
        (1, 10, 10, "asc"),  # 첫 번째 페이지, 10개씩, 10개 조회  예상
        (2, 10, 10, "desc"),  # 두 번째 페이지, 10개씩, 10개 조회 예상
        (1, 50, 20, "asc"),  # 세 번째 페이지, 50개씩, 20개 조회 예상
        (4, 6, 2, "asc"),  # 네 번째 페이지, 6개씩, 2개 조회 예상
        (3, 10, 0, "asc"),  # 세 번째 페이지, 10개씩, 데이터 없음
        (5, 5, 0, "asc"),  # 다섯 번째 페이지, 5개씩, 데이터 없음
    ],
)
def test__사용자는_상품_페이지네이션_결과를_확인할_수_있다(
    product_service, mock_db, default_user, current_page, per_page, expected_count, sort_by
):
    # get_all_products 호출
    all_products = product_service.get_all_products(
        based_on="product_no",
        sort_by=sort_by,
        current_page=current_page,
        per_page=per_page,
        db=mock_db,
    )

    total_products = 20
    start_index = (current_page - 1) * per_page

    if start_index >= total_products:
        assert len(all_products) == expected_count
    else:
        # 전체 상품 수 확인
        assert (
            len(all_products) == expected_count
        ), f"페이지당 반환된 상품 개수가 예상과 다릅니다: {len(all_products)} != {expected_count}"

    # 정렬된 전체 상품 리스트 시뮬레이션 (20개 상품)
    sorted_product_nos = list(range(1, total_products + 1))  # [1, 2, ..., 20]
    if sort_by == "desc":
        sorted_product_nos.reverse()

    # 현재 페이지의 시작 인덱스와 데이터 범위
    end_index = start_index + per_page
    expected_product_nos = [f"P{i}" for i in sorted_product_nos[start_index:end_index]]

    # 반환된 상품 번호 추출
    returned_product_nos = [product.id for product in all_products]

    # 반환된 상품 번호 확인
    assert (
        returned_product_nos == expected_product_nos
    ), f"페이지네이션 결과가 예상과 다릅니다: {returned_product_nos} != {expected_product_nos}"
