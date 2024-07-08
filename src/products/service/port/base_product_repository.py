from abc import ABC, abstractmethod

from sqlalchemy.orm import Session

from src.products.domain.product import Product
from src.products.routes.dto.response.title_with_link import TitleWithLink


class BaseProductRepository(ABC):

    @abstractmethod
    def get_rep_nms(self, product_id: str, db: Session) -> list[str]:
        pass

    @abstractmethod
    def get_product_detail(self, product_id: str, db: Session) -> Product:
        pass

    @abstractmethod
    def get_all_products(self, db: Session):
        pass

    @abstractmethod
    def get_links_by_product_code(
        self, product_id: str, link_type: str, db: Session
    ) -> list[TitleWithLink]:
        pass
