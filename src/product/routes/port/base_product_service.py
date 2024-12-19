from abc import ABC, abstractmethod

from sqlalchemy.orm import Session

from src.main.transactional import transactional
from src.product.infra.dto.product_search_condition import ProductSearchCondition
from src.product.routes.dto.request.product_link_update import ProductLinkUpdate
from src.product.routes.dto.request.product_update import ProductUpdate
from src.product.routes.dto.response.product_response import ProductResponse


class BaseProductService(ABC):

    @abstractmethod
    def get_product_detail(self, product_id, db: Session) -> ProductResponse:
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
    ) -> list[ProductResponse]:
        pass

    @transactional
    @abstractmethod
    def update_product_link(
        self, product_id: str, product_link_update: ProductLinkUpdate, db: Session
    ):
        pass

    @transactional
    @abstractmethod
    def update(self, product_id: str, product_update: ProductUpdate, db: Session):
        pass

    @abstractmethod
    def get_all_products_count(
        self, db, search_condition: ProductSearchCondition | None = None
    ) -> int:
        pass
