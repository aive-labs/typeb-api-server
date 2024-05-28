from abc import ABC, abstractmethod
from typing import Any

from pandas import DataFrame

from src.audiences.domain.audience import Audience
from src.audiences.infra.dto.linked_campaign import LinkedCampaign
from src.users.domain.user import User


class BaseAudienceRepository(ABC):

    @abstractmethod
    def get_audiences(
        self, user: User, is_exclude: bool | None = None
    ) -> tuple[list[dict[Any, Any]], DataFrame]:
        pass

    @abstractmethod
    def get_audience_stats(self, audience_id: str):
        pass

    @abstractmethod
    def get_audience_products(self, audience_id: str):
        pass

    @abstractmethod
    def get_audience_count(self, audience_id: str):
        pass

    @abstractmethod
    def get_audience(self, audience_id: str) -> Audience:
        pass

    @abstractmethod
    def get_linked_campaigns(self, audience_id: str) -> list[LinkedCampaign]:
        pass

    @abstractmethod
    def update_expired_audience_status(self, audience_id: str):
        pass

    @abstractmethod
    def delete_audience(self, audience_id: str):
        pass
