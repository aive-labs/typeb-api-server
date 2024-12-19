from sqlalchemy.orm import Session

from src.common.utils.get_env_variable import get_env_variable
from src.content.service.port.base_creatives_repository import BaseCreativesRepository
from src.main.exceptions.exceptions import ValidationException
from src.main.transactional import transactional
from src.product.domain.product import Product
from src.product.enums.product_link_type import ProductLinkType
from src.product.infra.dto.product_search_condition import ProductSearchCondition
from src.product.routes.dto.request.product_link_update import ProductLinkUpdate
from src.product.routes.dto.request.product_update import ProductUpdate
from src.product.routes.dto.response.product_response import ProductResponse
from src.product.routes.port.base_product_service import BaseProductService
from src.product.service.port.base_product_repository import BaseProductRepository


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

        product_response = ProductResponse.from_model(
            product, rep_nm, youtube_links, instagram_links
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
        search_condition: ProductSearchCondition | None = None,
    ) -> list[ProductResponse]:
        products = self.product_repository.get_all_products(
            based_on, sort_by, current_page, per_page, db=db, search_condition=search_condition
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

            product_response = ProductResponse.from_model(
                product, rep_nm, youtube_links, instagram_links
            )
            product_responses.append(product_response.set_creatives(creatives))

        return product_responses

    def get_all_products_count(
        self, db, search_condition: ProductSearchCondition | None = None
    ) -> int:
        return self.product_repository.get_all_products_count(
            db=db, search_condition=search_condition
        )

    @transactional
    def update_product_link(
        self, product_id: str, product_link_update: ProductLinkUpdate, db: Session
    ):
        self.product_repository.update_product_link(product_id, product_link_update, db)

    @transactional
    def update(self, product_id: str, product_update: ProductUpdate, db: Session):
        self.product_repository.update(product_id, product_update, db)
