from abc import ABC, abstractmethod

from sqlalchemy.orm import Session

from src.auth.domain.ga_integration import GAIntegration


class BaseGARepository(ABC):
    @abstractmethod
    def get_by_mall_id(self, mall_id: str, db: Session) -> GAIntegration:
        pass

    @abstractmethod
    def save_ga_integration(self, ga_integration: GAIntegration, db: Session):
        pass
