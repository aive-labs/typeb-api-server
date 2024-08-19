from abc import ABC, abstractmethod

from sqlalchemy.orm import Session

from src.core.transactional import transactional


class CustomerKeyUseCase(ABC):

    @abstractmethod
    def get_customer_key(self, mall_id, db: Session) -> str | None:
        pass

    @transactional
    @abstractmethod
    def save_customer_key(self, mall_id, customer_key, db: Session):
        pass
