from datetime import datetime

import pytest

from src.product.domain.product import Product
from src.product.service.product_service import ProductService
from test.unit.creatives.fixtures.mock_creatives_repository import (
    get_mock_creatives_repository,
)
from test.unit.products.fixtures.mock_product_repository import (
    get_mock_product_repository,
)


@pytest.fixture
def mock_product_repository():
    products = []

    for i in range(1, 21):
        product = Product(
            shop_no=1,
            product_no=1000 + i,
            product_code=f"P{i}",
            custom_product_code=f"CP{i:04d}",
            brand_code=f"BRC{i:03d}",
            trend_code=f"TC{i:03d}",
            product_name=f"상품명 {i}",
            eng_product_name=f"Product Name {i}",
            supply_product_name=f"공급 상품명 {i}",
            internal_product_name=f"내부 상품명 {i}",
            model_name=f"Model{i}",
            brand_name=f"브랜드 {i}",
            trend_name=f"트렌드 {i}",
            category_no=100 + i,
            category_name=f"카테고리 {i}",
            category_depth=str(i),
            full_category_name_1=f"카테고리1_{i}",
            full_category_name_2=f"카테고리2_{i}",
            full_category_name_3=f"카테고리3_{i}",
            full_category_name_4=f"카테고리4_{i}",
            full_category_no_1=f"1{i}",
            full_category_no_2=f"2{i}",
            full_category_no_3=f"3{i}",
            full_category_no_4=f"4{i}",
            is_bundle="Yes" if i % 2 == 0 else "No",
            made_date=datetime(2022, 1, i),
            release_date=datetime(2022, 2, i),
            created_date=datetime(2022, 3, i),
            detail_image=f"http://example.com/detail_{i}.jpg",
            list_image=f"http://example.com/list_{i}.jpg",
            tiny_image=f"http://example.com/tiny_{i}.jpg",
            small_image=f"http://example.com/small_{i}.jpg",
            additional_image=f"http://example.com/additional_{i}.jpg",
            display="T" if i % 2 == 0 else "F",
            selling="T",
            product_condition="New",
            sold_out="N",
            price=10000 + i * 1000,
            retail_price=12000 + i * 1000,
            additional_price=500,
            discountprice=9000 + i * 900,
            cloth_fabric="Cotton",
            product_material="Cotton",
            summary_description=f"요약 설명 {i}",
            simple_description=f"간단 설명 {i}",
            product_tag=f"태그{i}, 태그{i + 1}",
            buy_limit_by_product="No",
            single_purchase_restriction="No",
            adult_certification="No",
            expiration_date_start_date="2023-01-01",
            expiration_date_end_date="2024-01-01",
            options="색상: 빨강, 사이즈: M",
            variants=f"변형상품{i}",
            exposure_limit_type="None",
            exposure_group_list="그룹1",
            set_product_type="TypeA",
            shipping_fee_type="무료",
            main="Yes" if i == 1 else "No",
            memos=f"메모 {i}",
            hits=100 * i,
            seo=f"SEO 키워드 {i}",
            project_no=f"PRJ{i:03d}",
            exchange_info=f"교환 정보 {i}",
            additional_information=f"추가 정보 {i}",
            relational_product=f"관련 상품 {i}",
            comment=f"코멘트 {i}",
            recommend_yn="Y" if i % 2 == 0 else "N",
            rep_nm=f"rep_nm_{i}",
            created_at=f"2022-03-{i:02d} 10:00:00",
            updated_at=f"2022-04-{i:02d} 10:00:00",
            etltime=datetime.now(),
        )
        products.append(product)

    return get_mock_product_repository(products)


@pytest.fixture
def mock_creatives_repository():
    return get_mock_creatives_repository()


@pytest.fixture
def product_service(mock_product_repository, mock_creatives_repository):
    return ProductService(mock_product_repository, mock_creatives_repository)
