from abc import ABC, abstractmethod

from src.search.routes.dto.id_with_item_response import IdWithItem
from src.search.routes.dto.id_with_label_response import IdWithLabel
from src.users.domain.user import User


class BaseSearchService(ABC):

    @abstractmethod
    def search_audience_with_strategy_id(
        self, strategy_id: str, search_keyword, user: User, is_exclude=False
    ) -> list[IdWithLabel]:
        pass

    @abstractmethod
    def search_audience_without_strategy_id(
        self, audience_type_code: str, search_keyword, is_exclude=False
    ) -> list[IdWithLabel]:
        pass

    @abstractmethod
    def search_offers_search_of_sets(
        self, audience_type_code, strategy_id, keyword, user
    ) -> list[IdWithLabel]:
        pass

    @abstractmethod
    def search_offers(self, audience_type_code, keyword, user) -> list[IdWithLabel]:
        pass

    @abstractmethod
    def search_recommend_products(
        self, audience_type_code, keyword
    ) -> list[IdWithItem]:
        pass
