from datetime import datetime, timedelta

from sqlalchemy.orm import Session

from src.audiences.service.port.base_audience_repository import BaseAudienceRepository
from src.campaign.infra.campaign_repository import CampaignRepository
from src.common.infra.recommend_products_repository import RecommendProductsRepository
from src.common.timezone_setting import selected_timezone
from src.contents.infra.contents_repository import ContentsRepository
from src.offers.infra.offer_repository import OfferRepository
from src.products.infra.product_repository import ProductRepository
from src.search.routes.dto.id_with_item_response import (
    IdWithItem,
    IdWithItemDescription,
)
from src.search.routes.dto.id_with_label_response import IdWithLabel
from src.search.routes.dto.strategy_search_response import StrategySearchResponse
from src.search.routes.port.base_search_service import BaseSearchService
from src.strategy.infra.strategy_repository import StrategyRepository
from src.users.domain.user import User


class SearchService(BaseSearchService):

    def __init__(
        self,
        audience_repository: BaseAudienceRepository,
        recommend_products_repository: RecommendProductsRepository,
        offer_repository: OfferRepository,
        contents_repository: ContentsRepository,
        campaign_repository: CampaignRepository,
        product_repository: ProductRepository,
        strategy_repository: StrategyRepository,
    ):
        self.audience_repository = audience_repository
        self.recommend_products_repository = recommend_products_repository
        self.offer_repository = offer_repository
        self.contents_repository = contents_repository
        self.campaign_repository = campaign_repository
        self.product_repository = product_repository
        self.strategy_repository = strategy_repository

    def search_audience_with_strategy_id(
        self,
        strategy_id: str,
        search_keyword: str,
        user: User,
        db: Session,
        is_exclude=False,
    ) -> list[IdWithLabel]:
        audience_ids = self.audience_repository.get_audiences_ids_by_strategy_id(strategy_id, db)
        return self.audience_repository.get_audiences_by_condition(
            audience_ids, search_keyword, is_exclude, db
        )

    def search_audience_without_strategy_id(
        self,
        search_keyword,
        db: Session,
        is_exclude=False,
        target_strategy: str | None = None,
    ) -> list[IdWithLabel]:
        return self.audience_repository.get_audiences_by_condition_without_strategy_id(
            search_keyword, is_exclude, db, target_strategy
        )

    def search_offers_search_of_sets(self, strategy_id, keyword, user: User) -> list[IdWithLabel]:
        return self.offer_repository.get_search_offers_of_sets(strategy_id, keyword, user)

    def search_offers(self, keyword, user: User) -> list[IdWithLabel]:
        return self.offer_repository.get_search_offers(keyword, user)

    def search_recommend_products(self, keyword) -> list[IdWithItemDescription]:
        return self.recommend_products_repository.search_recommend_products(keyword)

    def search_contents_tag(self, keyword, recsys_model_id, db: Session) -> list[IdWithItem]:
        return self.contents_repository.search_contents_tag(keyword, recsys_model_id, db)

    def search_campaign(self, keyword, db) -> list[IdWithItem]:
        current_timestamp = datetime.now(selected_timezone)
        current_date = current_timestamp.strftime("%Y%m%d")
        two_weeks_ago = current_timestamp - timedelta(days=14)
        two_weeks_ago = two_weeks_ago.strftime("%Y%m%d")

        return self.campaign_repository.search_campaign(keyword, current_date, two_weeks_ago, db)

    def search_rep_nms(self, product_id, db) -> list[str]:
        return self.product_repository.get_rep_nms(product_id, db)

    def search_strategies(
        self, campaign_type_code, search_keyword, db: Session
    ) -> list[StrategySearchResponse]:
        return self.strategy_repository.search_keyword(campaign_type_code, search_keyword, db)

    def search_strategy_themes(self, strategy_id: str, db: Session) -> list[IdWithItem]:
        return self.strategy_repository.search_strategy_themes_by_strategy_id(strategy_id, db)
