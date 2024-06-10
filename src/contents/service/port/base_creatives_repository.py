from abc import ABC, abstractmethod
from typing import Any


class BaseCreativesRepository(ABC):
    @abstractmethod
    def find_by_id(self, id: int):
        pass

    @abstractmethod
    def find_all(self, based_on, sort_by, asset_type=None, query=None) -> list[Any]:
        pass

    @abstractmethod
    def get_simple_style_list(self) -> list:
        pass

    @abstractmethod
    def update_creatives(self, creative_id, creative_update, pre_fix):
        pass
