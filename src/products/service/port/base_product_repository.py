from abc import ABC, abstractmethod

from sqlalchemy.orm import Session


class BaseProductRepository(ABC):

    @abstractmethod
    def get_rep_nms(self, product_id: str, db: Session) -> list[str]:
        pass
