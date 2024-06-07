from src.strategy.infra.strategy_repository import StrategyRepository
from src.strategy.routes.dto.response.strategy_response import StrategyResponse
from src.strategy.routes.dto.response.strategy_with_campaign_theme_response import (
    StrategyWithCampaignThemeResponse,
)
from src.strategy.routes.port.get_strategy_usecase import GetStrategyUsecase
from src.users.domain.user import User


class GetStrategyService(GetStrategyUsecase):
    def __init__(self, strategy_repository: StrategyRepository):
        self.strategy_repository = strategy_repository

    def get_strategies(
        self, start_date: str, end_date: str, user: User
    ) -> list[StrategyResponse]:
        # TODO: 생성 부서 오브젝트 필터링 추가 작업 필요

        strategies = self.strategy_repository.get_all_strategies(
            start_date, end_date, user
        )

        return [StrategyResponse.from_model(model) for model in strategies]

    def get_strategy_detail(
        self, strategy_id: str
    ) -> StrategyWithCampaignThemeResponse:
        strategy, campaign_theme_obj = self.strategy_repository.get_strategy_detail(
            strategy_id
        )

        response = StrategyWithCampaignThemeResponse(
            strategy_name=strategy.strategy_name,
            strategy_tags=strategy.strategy_tags,
            strategy_metric_code=strategy.strategy_metric_code,
            strategy_metric_name=strategy.strategy_metric_name,
            strategy_status_code=strategy.strategy_status_code,
            strategy_status_name=strategy.strategy_status_name,
            audience_type_code=strategy.audience_type_code,
            audience_type_name=strategy.audience_type_name,
            target_group_code=strategy.target_group_code,
            target_group_name=strategy.target_group_name,
            campaign_themes=campaign_theme_obj,
            created_at=strategy.created_at,
            updated_at=strategy.updated_at,
        )

        return response
