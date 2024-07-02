from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from src.auth.utils.permission_checker import get_permission_checker
from src.core.container import Container
from src.core.database import get_db_session
from src.strategy.routes.dto.request.strategy_create import StrategyCreate
from src.strategy.routes.dto.response.strategy_response import StrategyResponse
from src.strategy.routes.port.create_strategy_usecase import CreateStrategyUseCase
from src.strategy.routes.port.delete_strategy_usecase import DeleteStrategyUseCase
from src.strategy.routes.port.get_strategy_usecase import GetStrategyUseCase
from src.strategy.routes.port.update_strategy_usecase import UpdateStrategyUseCase

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


@strategy_router.get("/strategies/{strategy_id}")
@inject
def read_strategy_object(
    strategy_id: str,
    get_strategy_service: GetStrategyUseCase = Depends(
        dependency=Provide[Container.get_strategy_service]
    ),
    user=Depends(get_permission_checker(required_permissions=[])),
):
    return get_strategy_service.get_strategy_detail(strategy_id)


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


@strategy_router.delete(
    "/strategies/{strategy_id}", status_code=status.HTTP_204_NO_CONTENT
)
@inject
def delete_strategy(
    strategy_id: str,
    db: Session = Depends(get_db_session),
    delete_strategy_service: DeleteStrategyUseCase = Depends(
        Provide[Container.delete_strategy_service]
    ),
):
    delete_strategy_service.exec(strategy_id, db=db)


@strategy_router.put("/strategies/{strategy_id}")
@inject
def update_strategy(
    strategy_id: str,
    strategy_update: StrategyCreate,
    db: Session = Depends(get_db_session),
    update_strategy_service: UpdateStrategyUseCase = Depends(
        Provide[Container.update_strategy_service]
    ),
):
    update_strategy_service.exec(strategy_id, strategy_update, db=db)
