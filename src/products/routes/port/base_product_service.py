from abc import ABC, abstractmethod

from sqlalchemy.orm import Session

from src.products.routes.dto.response.product_response import ProductResponse


class BaseProductService(ABC):

    @abstractmethod
    def get_product_detail(self, product_id, db: Session) -> ProductResponse:
        pass

    @abstractmethod
    def get_all_products(self, db: Session):
        pass
