from datetime import datetime, timedelta

from sqlalchemy import distinct, func
from sqlalchemy.orm import Session
from sqlalchemy.sql.functions import coalesce

from src.audiences.infra.entity.audience_customer_mapping_entity import (
    AudienceCustomerMappingEntity,
)
from src.audiences.infra.entity.variable_table_list import CustomerInfoStatusEntity
from src.audiences.service.port.base_audience_repository import BaseAudienceRepository
from src.campaign.infra.campaign_repository import CampaignRepository
from src.common.infra.recommend_products_repository import RecommendProductsRepository
from src.common.timezone_setting import selected_timezone
from src.contents.infra.contents_repository import ContentsRepository
from src.core.exceptions.exceptions import ConsistencyException
from src.offers.infra.entity.offers_entity import OffersEntity
from src.offers.infra.offer_repository import OfferRepository
from src.products.infra.product_repository import ProductRepository
from src.search.routes.dto.id_with_item_response import (
    IdWithItem,
    IdWithItemDescription,
)
from src.search.routes.dto.id_with_label_response import IdWithLabel
from src.search.routes.dto.reviewer_response import ReviewerResponse
from src.search.routes.dto.send_user_response import SendUserResponse
from src.search.routes.dto.strategy_search_response import StrategySearchResponse
from src.search.routes.port.base_search_service import BaseSearchService
from src.strategy.infra.entity.strategy_theme_entity import StrategyThemesEntity
from src.strategy.infra.strategy_repository import StrategyRepository
from src.users.domain.user import User
from src.users.infra.user_repository import UserRepository


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
        user_repository: UserRepository,
    ):
        self.audience_repository = audience_repository
        self.recommend_products_repository = recommend_products_repository
        self.offer_repository = offer_repository
        self.contents_repository = contents_repository
        self.campaign_repository = campaign_repository
        self.product_repository = product_repository
        self.strategy_repository = strategy_repository
        self.user_repository = user_repository

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

    def search_send_users(self, db: Session, keyword=None) -> list[SendUserResponse]:
        return self.user_repository.get_send_users(db, keyword)

    def search_reviewer(self, user, db: Session, keyword) -> list[ReviewerResponse]:
        # 임시로 본인 넣어둠

        user_info = self.user_repository.get_user_by_id(user.user_id, db)

        if user_info.user_id is None:
            raise ConsistencyException(detail={"message": "사용자 정보를 조회할 수 없습니다."})

        return [
            ReviewerResponse(
                user_id=user_info.user_id,
                user_name_object=f"{user_info.username}/{user_info.department_name}",
                test_callback_number=(
                    user_info.test_callback_number if user_info.test_callback_number else ""
                ),
                default_reviewer_yn="n",
            )
        ]

    def search_campaign_set_items(
        self, strategy_theme_id, audience_id, coupon_no, db: Session
    ) -> list[str]:
        # 세트 추가 시, 선택한 strategy_theme_id, audience_id, coupon_no 해당하는 추천 대표상품목록

        # 1. 오퍼 조회
        offers = (
            db.query(
                OffersEntity.benefit_type,
                func.min(
                    coalesce(OffersEntity.benefit_price, OffersEntity.benefit_percentage)
                ).label("offer_amount"),
            )
            .filter(OffersEntity.coupon_no == coupon_no)
            .group_by(OffersEntity.benefit_type)
        )

        # 2. 추천 모델 조회
        recsys_model_id = (
            db.query(StrategyThemesEntity.recsys_model_id)
            .filter(StrategyThemesEntity.strategy_theme_id == strategy_theme_id)
            .scalar()
        )

        # 3. rep_nm_list 생성 <- cus_info_status, offer 조인, audience 조인
        # 조회에 추천 모델 컬럼까지 선택
        # TODO recsys_model_id에 따라서 어떤 컬럼을 선택할지 지정
        columns_of_interest = [
            CustomerInfoStatusEntity.first_best_items,
            CustomerInfoStatusEntity.best_promo_items,
            CustomerInfoStatusEntity.best_gender_items,
            CustomerInfoStatusEntity.best_category_items,
            CustomerInfoStatusEntity.best_age_items,
            CustomerInfoStatusEntity.best_new_items,
            CustomerInfoStatusEntity.steady_items,
            CustomerInfoStatusEntity.best_cross_items,
        ]

        recommend_rep_nm_set = set()

        for column in columns_of_interest:
            subquery = (
                db.query(distinct(column))
                .join(
                    AudienceCustomerMappingEntity,
                    CustomerInfoStatusEntity.cus_cd == AudienceCustomerMappingEntity.cus_cd,
                )
                .filter(AudienceCustomerMappingEntity.audience_id == audience_id)
                .subquery()
            )

            results = db.query(subquery).all()
            recommend_rep_nm_set.update([result[0] for result in results if result[0] is not None])

        # Convert the set to a list (if needed)
        recommend_rep_nm_list = list(recommend_rep_nm_set)

        return recommend_rep_nm_list
