from abc import ABC, abstractmethod

from sqlalchemy.orm import Session

from src.common.domain.recsys_models import RecsysModels


class BaseCommonRepository(ABC):
    @abstractmethod
    def get_recsys_model(self, recsys_model_id: int, db: Session) -> RecsysModels:
        pass

    @abstractmethod
    def get_all_customer_count(self, db: Session) -> int:
        pass
