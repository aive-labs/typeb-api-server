from sqlalchemy.orm import Session

from src.audiences.service.port.base_audience_repository import BaseAudienceRepository
from src.common.infra.recommend_products_repository import RecommendProductsRepository
from src.contents.infra.contents_repository import ContentsRepository
from src.offers.infra.offer_repository import OfferRepository
from src.search.routes.dto.id_with_item_response import (
    IdWithItem,
    IdWithItemDescription,
)
from src.search.routes.dto.id_with_label_response import IdWithLabel
from src.search.routes.port.base_search_service import BaseSearchService
from src.users.domain.user import User


class SearchService(BaseSearchService):

    def __init__(
        self,
        audience_repository: BaseAudienceRepository,
        recommend_products_repository: RecommendProductsRepository,
        offer_repository: OfferRepository,
        contents_repository: ContentsRepository,
    ):
        self.audience_repository = audience_repository
        self.recommend_products_repository = recommend_products_repository
        self.offer_repository = offer_repository
        self.contents_repository = contents_repository

    def search_audience_with_strategy_id(
        self, strategy_id: str, search_keyword: str, user: User, is_exclude=False
    ) -> list[IdWithLabel]:
        audience_ids = self.audience_repository.get_audiences_ids_by_strategy_id(
            strategy_id
        )
        return self.audience_repository.get_audiences_by_condition(
            audience_ids, search_keyword, is_exclude
        )

    def search_audience_without_strategy_id(
        self, search_keyword, is_exclude=False, target_strategy: str | None = None
    ) -> list[IdWithLabel]:
        return self.audience_repository.get_audiences_by_condition_without_strategy_id(
            search_keyword, is_exclude, target_strategy
        )

    def search_offers_search_of_sets(
        self, strategy_id, keyword, user: User
    ) -> list[IdWithLabel]:
        return self.offer_repository.get_search_offers_of_sets(
            strategy_id, keyword, user
        )

    def search_offers(self, keyword, user: User) -> list[IdWithLabel]:
        return self.offer_repository.get_search_offers(keyword, user)

    def search_recommend_products(self, keyword) -> list[IdWithItemDescription]:
        return self.recommend_products_repository.search_recommend_products(keyword)

    def search_contents_tag(
        self, keyword, recsys_model_id, db: Session
    ) -> list[IdWithItem]:
        return self.contents_repository.search_contents_tag(
            keyword, recsys_model_id, db
        )
