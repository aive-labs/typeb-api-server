from sqlalchemy.orm import Session

from src.common.utils.get_env_variable import get_env_variable
from src.contents.service.port.base_creatives_repository import BaseCreativesRepository
from src.core.exceptions.exceptions import ValidationException
from src.core.transactional import transactional
from src.products.domain.product import Product
from src.products.enums.product_link_type import ProductLinkType
from src.products.routes.dto.request.product_link_update import ProductLinkUpdate
from src.products.routes.dto.request.product_update import ProductUpdate
from src.products.routes.dto.response.product_response import ProductResponse
from src.products.routes.port.base_product_service import BaseProductService
from src.products.service.port.base_product_repository import BaseProductRepository


class ProductService(BaseProductService):

    def __init__(
        self,
        product_repository: BaseProductRepository,
        creatives_repository: BaseCreativesRepository,
    ):
        self.product_repository = product_repository
        self.creatives_repository = creatives_repository
        self.cloud_front_url = get_env_variable("cloud_front_asset_url")

    def get_product_detail(self, product_id, db: Session) -> ProductResponse:
        product: Product = self.product_repository.get_product_detail(product_id, db)
        rep_nm = self.product_repository.get_rep_nms(product_id, db)
        youtube_links = self.product_repository.get_links_by_product_code(
            product_id, ProductLinkType.YOUTUBE.value, db
        )
        instagram_links = self.product_repository.get_links_by_product_code(
            product_id, ProductLinkType.INSTAGRAM.value, db
        )

        creatives = self.creatives_repository.get_creatives_by_style_cd(style_cd=product_id, db=db)

        for creative in creatives:
            creative.set_image_url(f"{self.cloud_front_url}/{creative.image_path}")

        product_response = ProductResponse(
            name=product.product_name,
            rep_nm=rep_nm[0] if rep_nm else None,
            category_1=product.full_category_name_1,
            category_2=product.full_category_name_2,
            category_3=product.full_category_name_3,
            category_4=product.full_category_name_4,
            comment=product.comment,
            recommend_yn=product.recommend_yn,
            price=product.price,
            discount_price=product.discountprice,
            sale_status=product.product_condition,
            sale_yn=product.display,
            youtube=youtube_links,
            instagram=instagram_links,
            created_at=product.created_at,
            updated_at=product.updated_at,
        )

        product_response = product_response.set_creatives(creatives)

        return product_response

    def get_all_products(
        self,
        based_on: str,
        sort_by: str,
        current_page: int,
        per_page: int,
        db: Session,
        keyword: str | None = None,
    ) -> list[ProductResponse]:
        products = self.product_repository.get_all_products(
            based_on, sort_by, current_page, per_page, db=db, keyword=keyword
        )

        product_responses = []
        for product in products:
            product_id = product.product_code

            if product_id is None:
                raise ValidationException("프로덕트 코드가 존재하지 않는 상품이 있습니다.")

            rep_nm = self.product_repository.get_rep_nms(product_id, db)
            youtube_links = self.product_repository.get_links_by_product_code(
                product_id, ProductLinkType.YOUTUBE.value, db
            )
            instagram_links = self.product_repository.get_links_by_product_code(
                product_id, ProductLinkType.INSTAGRAM.value, db
            )

            creatives = self.creatives_repository.get_creatives_by_style_cd(
                style_cd=product_id, db=db
            )

            for creative in creatives:
                creative.set_image_url(f"{self.cloud_front_url}/{creative.image_path}")

            product_response = ProductResponse(
                name=product.product_name,
                rep_nm=rep_nm[0] if rep_nm else None,
                category_1=product.full_category_name_1,
                category_2=product.full_category_name_2,
                category_3=product.full_category_name_3,
                category_4=product.full_category_name_4,
                comment=product.comment,
                recommend_yn=product.recommend_yn,
                price=product.price,
                discount_price=product.discountprice,
                sale_status=product.product_condition,
                sale_yn=product.display,
                youtube=youtube_links,
                instagram=instagram_links,
                created_at=product.created_at,
                updated_at=product.updated_at,
            )

            product_responses.append(product_response.set_creatives(creatives))

        return product_responses

    def get_all_products_count(self, db) -> int:
        return self.product_repository.get_all_products_count(db)

    @transactional
    def update_product_link(
        self, product_id: str, product_link_update: ProductLinkUpdate, db: Session
    ):
        self.product_repository.update_product_link(product_id, product_link_update, db)

    @transactional
    def update(self, product_id: str, product_update: ProductUpdate, db: Session):
        self.product_repository.update(product_id, product_update, db)
