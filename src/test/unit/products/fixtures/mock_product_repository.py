from unittest.mock import MagicMock

from src.products.domain.product import Product
from src.products.infra.dto.product_search_condition import ProductSearchCondition
from src.products.routes.dto.request.product_link_update import ProductLinkUpdate
from src.products.routes.dto.request.product_update import ProductUpdate
from src.products.service.port.base_product_repository import BaseProductRepository


def get_mock_product_repository(mock_products):
    mock_repository = MagicMock(spec_set=BaseProductRepository)

    products: list[Product] = mock_products

    def get_rep_nms(product_id: str, db):
        filtered_products = [product for product in products if product.product_code == product_id]
        return list({product.rep_nm for product in filtered_products if product.rep_nm is not None})

    def get_product_detail(product_id: str, db):
        product = [product for product in products if product.product_code == product_id]
        return Product.model_validate(product[0])

    def get_all_products(
        based_on: str,
        sort_by: str,
        current_page: int,
        per_page: int,
        db,
        search_condition: ProductSearchCondition | None = None,
    ):

        filtered_products = filter_search_condition(search_condition)

        reverse = True if sort_by == "desc" else False
        filtered_products.sort(key=lambda x: getattr(x, based_on) or 0, reverse=reverse)

        # Apply pagination (offset and limit)
        offset = (current_page - 1) * per_page
        limit = per_page
        paginated_products = filtered_products[offset : (offset + limit)]

        return paginated_products

    def update_product_link(product_id, product_link_update: ProductLinkUpdate, db):
        pass

    def update(product_id, product_update: ProductUpdate, db):
        pass

    def get_all_products_count(db, search_condition: ProductSearchCondition | None = None):
        products = filter_search_condition(search_condition)
        return len(products)

    def filter_search_condition(search_condition):

        if search_condition:
            keyword = search_condition.get("keyword", "").lower()
            rep_nm = search_condition.get("rep_nm", "")
            rep_nm_list = [name.strip() for name in rep_nm.split(",")] if rep_nm else []
            recommend_yn = search_condition.get("recommend_yn", "")
            sale_yn = search_condition.get("sale_yn", "")

            if sale_yn:
                sale_yn_mapping = "T" if sale_yn == "Y" else "F"
            else:
                sale_yn_mapping = None

            def condition(product: Product):
                keyword_match = True
                rep_nm_match = True
                recommend_yn_match = True
                sale_yn_match = True

                # Check for keyword match in product_code or product_name
                if keyword:
                    keyword_match = (
                        keyword in (product.product_code or "").lower()
                        or keyword in (product.product_name or "").lower()
                    )

                # Check for rep_nm match
                if rep_nm_list:
                    rep_nm_match = product.rep_nm in rep_nm_list

                # Check for recommend_yn match
                if recommend_yn:
                    recommend_yn_match = product.recommend_yn == recommend_yn

                # Check for sale_yn match
                if sale_yn_mapping:
                    sale_yn_match = product.selling == sale_yn_mapping

                return keyword_match and rep_nm_match and recommend_yn_match and sale_yn_match

            filtered_products = filter(condition, products)
            return list(filtered_products)

        return products

    def get_links_by_product_code(product_id: str, link_type: str, db):
        pass

    mock_repository.get_product_detail.side_effect = get_product_detail
    mock_repository.get_all_products.side_effect = get_all_products
    mock_repository.get_all_products_count.side_effect = get_all_products_count
    mock_repository.update_product_link.side_effect = update_product_link
    mock_repository.update.side_effect = update
    mock_repository.get_rep_nms.side_effect = get_rep_nms

    return mock_repository
