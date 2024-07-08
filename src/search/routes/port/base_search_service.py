from abc import ABC, abstractmethod

from sqlalchemy.orm import Session

from src.search.routes.dto.id_with_item_response import (
    IdWithItem,
    IdWithItemDescription,
)
from src.search.routes.dto.id_with_label_response import IdWithLabel
from src.users.domain.user import User


class BaseSearchService(ABC):

    @abstractmethod
    def search_audience_with_strategy_id(
        self,
        strategy_id: str,
        search_keyword,
        user: User,
        db: Session,
        is_exclude=False,
    ) -> list[IdWithLabel]:
        pass

    @abstractmethod
    def search_audience_without_strategy_id(
        self,
        search_keyword,
        db: Session,
        is_exclude=False,
        target_strategy: str | None = None,
    ) -> list[IdWithLabel]:
        pass

    @abstractmethod
    def search_offers_search_of_sets(
        self, strategy_id, keyword, user
    ) -> list[IdWithLabel]:
        pass

    @abstractmethod
    def search_offers(self, keyword, user) -> list[IdWithLabel]:
        pass

    @abstractmethod
    def search_recommend_products(self, keyword) -> list[IdWithItemDescription]:
        pass

    @abstractmethod
    def search_contents_tag(
        self, keyword, recsys_model_id, db: Session
    ) -> list[IdWithItem]:
        pass

    @abstractmethod
    def search_campaign(self, keyword, db) -> list[IdWithItem]:
        pass

    @abstractmethod
    def search_rep_nms(self, product_id, db) -> list[str]:
        pass
