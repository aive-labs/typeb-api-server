from sqlalchemy.orm import Session

from src.core.exceptions.exceptions import (
    DuplicatedException,
    LinkedCampaignException,
    ValidationException,
)
from src.core.transactional import transactional
from src.strategy.domain.strategy import Strategy
from src.strategy.domain.strategy_theme import (
    StrategyTheme,
    StrategyThemeAudienceMapping,
    StrategyThemeOfferMapping,
)
from src.strategy.enums.recommend_model import RecommendModels
from src.strategy.enums.strategy_status import StrategyStatus
from src.strategy.infra.strategy_repository import StrategyRepository
from src.strategy.routes.dto.request.strategy_create import StrategyCreate
from src.strategy.routes.port.update_strategy_usecase import UpdateStrategyUseCase
from src.users.domain.user import User


class UpdateStrategyService(UpdateStrategyUseCase):

    def __init__(self, strategy_repository: StrategyRepository):
        self.strategy_repository = strategy_repository

    @transactional
    def exec(self, strategy_id: str, strategy_update: StrategyCreate, user: User, db: Session):
        """전략 수정 함수

        -연결된 캠페인이 존재하는 경우
            - 수정 불가. error raise

        -수정 테이블:
        1. strategies
        2. campaign_themes
        3. themes_audiences_mapping
        4. strategy_cond_list
        """

        strategy, _ = self.strategy_repository.get_strategy_detail(strategy_id, db)

        self._check_linked_campaign(strategy)
        self._check_duplicate_name(strategy_id, strategy_update, db)

        audience_ids = []
        for theme in strategy_update.strategy_themes:
            audience_ids.extend(theme.theme_audience_set.audience_ids)

        self._is_duplicate_audience_selected(audience_ids)

        update_strategy = Strategy.from_update(strategy_id, strategy_update)
        update_strategy_themes: list[StrategyTheme] = []
        recommend_model_ids: list[int] = []

        for _, theme in enumerate(strategy_update.strategy_themes):
            # 입력값 및 비즈니스 로직에 대한 예외 검증
            self._check_strategy_theme_validation(recommend_model_ids, strategy_update, theme)

            theme_audience = [
                StrategyThemeAudienceMapping(
                    audience_id=audience_id,
                    strategy_theme_id=theme.strategy_theme_id,
                    updated_by=user.username,
                )
                for audience_id in theme.theme_audience_set.audience_ids
            ]

            theme_offer = [
                StrategyThemeOfferMapping(
                    coupon_no=coupon_no,
                    strategy_theme_id=theme.strategy_theme_id,
                    updated_by=user.username,
                )
                for coupon_no in theme.theme_audience_set.coupon_no_list
            ]

            update_strategy_themes.append(
                StrategyTheme(
                    strategy_theme_id=theme.strategy_theme_id,
                    strategy_theme_name=theme.strategy_theme_name,
                    recsys_model_id=theme.recsys_model_id,
                    strategy_id=strategy_id,
                    contents_tags=theme.theme_audience_set.contents_tags,
                    strategy_theme_audience_mapping=theme_audience,
                    strategy_theme_offer_mapping=theme_offer,
                    updated_by=user.username,
                )
            )

        self.strategy_repository.update(update_strategy, update_strategy_themes, user, db)

    def _is_duplicate_audience_selected(self, audience_ids):
        if len(audience_ids) != len(set(audience_ids)):
            raise DuplicatedException(
                detail={
                    "code": "strategy/create",
                    "message": "같은 오디언스가 중복으로 사용되었습니다.",
                },
            )

    def _check_duplicate_name(self, strategy_id, strategy_update, db):
        if self.strategy_repository.is_strategy_name_exists_for_update(
            strategy_id, strategy_update.strategy_name, db
        ):
            raise DuplicatedException(
                detail={
                    "code": "strategy/create",
                    "message": "동일한 전략명이 존재합니다.",
                },
            )

    def _check_linked_campaign(self, strategy):
        if strategy.strategy_status_code == StrategyStatus.active.value:
            raise LinkedCampaignException(
                detail={
                    "code": "modify/01",
                    "message": "수정 불가 - 연결된 캠페인이 존재합니다.",
                }
            )

    def _check_duplicate_recommend_model(self, recommend_model_id: int, recommend_model_list):
        """Checks for duplicate recommender system model IDs and raises an exception if found."""
        if recommend_model_id != 0 and (recommend_model_id in recommend_model_list):
            raise DuplicatedException(
                detail={
                    "code": "strategy/create",
                    "message": "추천 모델이 중복으로 사용되었습니다.",
                },
            )

    def _check_exclusive_new_collection_model(self, recommend_model_list):
        """Checks if the new collection recommendation model is used exclusively and raises an exception if not."""
        if (RecommendModels.NEW_COLLECTION.value in recommend_model_list) and len(
            set(recommend_model_list)
        ) > 1:
            raise ValidationException(
                detail={
                    "code": "strategy/create",
                    "message": "신상품 추천 모델은 전략 내 단독으로만 사용 가능합니다. (다른 추천 모델 사용 불가)",
                },
            )

    def _check_strategy_theme_validation(self, recommend_model_ids, strategy_create, theme):
        # 1. 테마모델 중복 점검
        self._check_duplicate_recommend_model(
            recommend_model_id=theme.recsys_model_id,
            recommend_model_list=recommend_model_ids,
        )
        recommend_model_ids.append(theme.recsys_model_id)
        # 2. 세그먼트 캠페인 - 신상품 추천 모델 단독 사용 점검
        self._check_exclusive_new_collection_model(recommend_model_list=recommend_model_ids)
