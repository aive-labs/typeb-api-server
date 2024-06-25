from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends

from src.auth.utils.permission_checker import get_permission_checker
from src.core.container import Container
from src.strategy.routes.dto.request.strategy_create import StrategyCreate
from src.strategy.routes.dto.response.strategy_response import StrategyResponse
from src.strategy.routes.dto.response.strategy_with_campaign_theme_response import (
    StrategyWithCampaignThemeResponse,
)
from src.strategy.routes.port.create_strategy_usecase import CreateStrategyUseCase
from src.strategy.routes.port.get_strategy_usecase import GetStrategyUseCase

strategy_router = APIRouter(tags=["Strategy-management"])


@strategy_router.get("/strategies")
@inject
def get_strategies(
    start_date: str,
    end_date: str,
    get_strategy_service: GetStrategyUseCase = Depends(
        dependency=Provide[Container.get_strategy_service]
    ),
    user=Depends(get_permission_checker(required_permissions=[])),
) -> list[StrategyResponse]:
    return get_strategy_service.get_strategies(start_date, end_date, user)


@strategy_router.post("/strategies")
@inject
def create_strategies(
    strategy_create: StrategyCreate,
    create_strategy_service: CreateStrategyUseCase = Depends(
        dependency=Provide[Container.create_strategy_service]
    ),
    user=Depends(
        get_permission_checker(
            required_permissions=["gnb_permissions:strategy_manager:create"]
        )
    ),
):
    result = create_strategy_service.create_strategy_object(strategy_create, user)
    return result


@strategy_router.get(
    "/strategies/{strategy_id}", response_model=StrategyWithCampaignThemeResponse
)
@inject
def read_strategy_object(
    strategy_id: str,
    user=Depends(
        get_permission_checker(
            required_permissions=["gnb_permissions:strategy_manager:read"]
        )
    ),
):
    pass
