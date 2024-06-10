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
