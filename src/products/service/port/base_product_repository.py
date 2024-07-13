from abc import ABC, abstractmethod

from sqlalchemy.orm import Session

from src.products.domain.product import Product
from src.products.infra.dto.product_search_condition import ProductSearchCondition
from src.products.routes.dto.response.title_with_link import TitleWithLink


class BaseProductRepository(ABC):

    @abstractmethod
    def get_rep_nms(self, product_id: str, db: Session) -> list[str]:
        pass

    @abstractmethod
    def get_product_detail(self, product_id: str, db: Session) -> Product:
        pass

    @abstractmethod
    def get_all_products(
        self,
        based_on: str,
        sort_by: str,
        current_page: int,
        per_page: int,
        db: Session,
        search_condition: ProductSearchCondition | None = None,
    ) -> list[Product]:
        pass

    @abstractmethod
    def get_links_by_product_code(
        self, product_id: str, link_type: str, db: Session
    ) -> list[TitleWithLink]:
        pass

    @abstractmethod
    def update_product_link(self, product_id, product_link_update, db):
        pass

    @abstractmethod
    def update(self, product_id, product_update, db):
        pass

    @abstractmethod
    def get_all_products_count(
        self, db, search_condition: ProductSearchCondition | None = None
    ) -> int:
        pass
