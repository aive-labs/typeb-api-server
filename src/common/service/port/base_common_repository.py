from abc import ABC, abstractmethod

from src.common.domain.recsys_models import RecsysModels


class BaseCommonRepository(ABC):
    @abstractmethod
    def get_recsys_model(self, recsys_model_id: int) -> RecsysModels:
        pass
