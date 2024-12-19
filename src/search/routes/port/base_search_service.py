from abc import ABC, abstractmethod
from typing import Optional

from sqlalchemy.orm import Session

from src.search.routes.dto.id_with_item_response import (
    IdWithItem,
    IdWithItemDescription,
)
from src.search.routes.dto.id_with_label_response import IdWithLabel
from src.search.routes.dto.reviewer_response import ReviewerResponse
from src.search.routes.dto.send_user_response import SendUserResponse
from src.search.routes.dto.strategy_search_response import StrategySearchResponse
from src.user.domain.user import User


class BaseSearchService(ABC):

    @abstractmethod
    def search_audience_with_strategy_id(
        self,
        strategy_id: str,
        search_keyword,
        user: User,
        db: Session,
        is_exclude=False,
        strategy_theme_id: str | None = None,
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
        self,
        strategy_id,
        keyword,
        user,
        db: Session,
        strategy_theme_id: Optional[str] = None,
    ) -> list[IdWithLabel]:
        pass

    @abstractmethod
    def search_offers(self, keyword, user, db: Session) -> list[IdWithLabel]:
        pass

    @abstractmethod
    def search_recommend_products(self, keyword, db: Session) -> list[IdWithItemDescription]:
        pass

    @abstractmethod
    def search_contents_tag(self, keyword, recsys_model_id, db: Session) -> list[IdWithItem]:
        pass

    @abstractmethod
    def search_campaign(self, keyword, db) -> list[IdWithItem]:
        pass

    @abstractmethod
    def search_rep_nms(self, product_id, db) -> list[str]:
        pass

    @abstractmethod
    def search_strategies(
        self, campaign_type_code, search_keyword, db: Session
    ) -> list[StrategySearchResponse]:
        pass

    @abstractmethod
    def search_strategy_themes(self, strategy_id: str, db: Session) -> list[IdWithItem]:
        pass

    @abstractmethod
    def search_send_users(self, db: Session, keyword=None) -> list[SendUserResponse]:
        pass

    @abstractmethod
    def search_reviewer(self, user, db: Session, keyword) -> list[ReviewerResponse]:
        pass

    @abstractmethod
    def search_campaign_set_items(
        self, strategy_theme_id, audience_id, coupon_no, db: Session
    ) -> list[str]:
        pass

    @abstractmethod
    def search_contents(
        self, strategy_theme_id: int, db: Session, keyword: str | None = None
    ) -> list:
        pass
