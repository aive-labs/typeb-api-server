from sqlalchemy.orm import Session

from src.core.exceptions.exceptions import DuplicatedException, ValidationException
from src.strategy.domain.strategy import Strategy
from src.strategy.domain.strategy_theme import (
    StrategyTheme,
    StrategyThemeAudienceMapping,
    StrategyThemeOfferMapping,
)
from src.strategy.enums.recommend_model import RecommendModels
from src.strategy.infra.strategy_repository import StrategyRepository
from src.strategy.routes.dto.request.strategy_create import StrategyCreate
from src.strategy.routes.port.create_strategy_usecase import CreateStrategyUseCase
from src.users.domain.user import User


class CreateStrategyService(CreateStrategyUseCase):
    def __init__(self, strategy_repository: StrategyRepository):
        self.strategy_repository = strategy_repository

    def create_strategy_object(self, strategy_create: StrategyCreate, user: User, db: Session):
        # 1. 전략명 중복 확인
        strategy_name = strategy_create.strategy_name
        if self.strategy_repository.is_strategy_name_exists(strategy_name, db):
            raise DuplicatedException(
                detail={
                    "code": "strategy/create",
                    "message": "동일한 전략명이 존재합니다.",
                },
            )

        # StrategyCreate 인스턴스에서 audience_ids 추출
        audience_ids = []
        for theme in strategy_create.strategy_themes:
            audience_ids.extend(theme.theme_audience_set.audience_ids)

        # 3. 어떤 경우에 어쩌고 저쩌고를 함
        if self.is_duplicate_audience_selected(audience_ids):
            raise DuplicatedException(
                detail={
                    "code": "strategy/create",
                    "message": "같은 오디언스가 중복으로 사용되었습니다.",
                },
            )

        # 4. 전략 도메인 생성
        new_strategy = Strategy.from_create(strategy_create)

        # 6. 캠페인 테마 수만큼 반복
        strategy_themes: list[StrategyTheme] = []
        recommend_model_ids: list[int] = []
        for _, theme in enumerate(strategy_create.strategy_themes):
            # 입력값 및 비즈니스 로직에 대한 예외 검증
            self._check_strategy_theme_validation(recommend_model_ids, strategy_create, theme)

            theme_audience = [
                StrategyThemeAudienceMapping(audience_id=audience_id)
                for audience_id in theme.theme_audience_set.audience_ids
            ]

            theme_offer = [
                StrategyThemeOfferMapping(coupon_no=coupon_no)
                for coupon_no in theme.theme_audience_set.coupon_no_list
            ]

            strategy_themes.append(
                StrategyTheme(
                    strategy_theme_name=theme.strategy_theme_name,
                    recsys_model_id=theme.recsys_model_id,
                    contents_tags=theme.theme_audience_set.contents_tags,
                    strategy_theme_audience_mapping=theme_audience,
                    strategy_theme_offer_mapping=theme_offer,
                )
            )

        self.strategy_repository.create_strategy(new_strategy, strategy_themes, user)

    def is_duplicate_audience_selected(self, audience_ids):
        return len(audience_ids) != len(set(audience_ids))

    def _check_strategy_theme_validation(self, recommend_model_ids, strategy_create, theme):
        # 1. 테마모델 중복 점검
        self._check_duplicate_recommend_model(
            recommend_model_id=theme.recsys_model_id,
            recommend_model_list=recommend_model_ids,
        )
        recommend_model_ids.append(theme.recsys_model_id)
        # 2. 세그먼트 캠페인 - 신상품 추천 모델 단독 사용 점검
        self._check_exclusive_new_collection_model(recommend_model_list=recommend_model_ids)

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
        if (RecommendModels.new_collection_rec.value in recommend_model_list) and len(
            set(recommend_model_list)
        ) > 1:
            raise ValidationException(
                detail={
                    "code": "strategy/create",
                    "message": "신상품 추천 모델은 전략 내 단독으로만 사용 가능합니다. (다른 추천 모델 사용 불가)",
                },
            )
