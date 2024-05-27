from abc import ABC, abstractmethod
from typing import Any

from pandas import DataFrame

from src.users.domain.user import User


class BaseAudienceRepository(ABC):

    @abstractmethod
    def get_audience(
        self, user: User, is_exclude: bool | None = None
    ) -> tuple[list[dict[Any, Any]], DataFrame]:
        pass

    @abstractmethod
    def get_audience_stats(self, audience_id: int):
        pass

    @abstractmethod
    def get_audience_products(self, audience_id: int):
        pass

    @abstractmethod
    def get_audience_count(self, audience_id: int):
        pass
