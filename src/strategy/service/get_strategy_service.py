from sqlalchemy.orm import Session

from src.main.exceptions.exceptions import ConvertException
from src.strategy.infra.strategy_repository import StrategyRepository
from src.strategy.model.response.strategy_response import StrategyResponse
from src.strategy.model.response.strategy_with_campaign_theme_response import (
    StrategyWithStrategyThemeResponse,
)
from src.strategy.routes.port.get_strategy_usecase import GetStrategyUseCase
from src.user.domain.user import User


class GetStrategyService(GetStrategyUseCase):
    def __init__(self, strategy_repository: StrategyRepository):
        self.strategy_repository = strategy_repository

    def get_strategies(
        self, start_date: str, end_date: str, user: User, db: Session
    ) -> list[StrategyResponse]:
        # TODO: 생성 부서 오브젝트 필터링 추가 작업 필요

        strategies = self.strategy_repository.get_all_strategies(start_date, end_date, user, db)

        return [StrategyResponse.from_model(model) for model in strategies]

    def get_strategy_detail(
        self, strategy_id: str, db: Session
    ) -> StrategyWithStrategyThemeResponse:
        strategy, strategy_themes = self.strategy_repository.get_strategy_detail(strategy_id, db)

        if strategy.created_at is None or strategy.updated_at is None:
            raise ConvertException(detail={"message": "created_at and updated_at cannot be None"})

        response = StrategyWithStrategyThemeResponse(
            strategy_name=strategy.strategy_name,
            strategy_tags=strategy.strategy_tags,
            strategy_status_code=strategy.strategy_status_code,
            strategy_status_name=strategy.strategy_status_name,
            target_strategy=strategy.target_strategy,
            strategy_themes=strategy_themes,
            created_at=strategy.created_at,
            updated_at=strategy.updated_at,
        )

        return response
