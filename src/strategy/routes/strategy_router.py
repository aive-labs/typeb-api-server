from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from src.auth.utils.permission_checker import get_permission_checker
from src.campaign.routes.port.generate_message_usecase import GenerateMessageUsecase  ##
from src.main.container import Container
from src.main.db_dependency import get_db
from src.strategy.routes.dto.request.preview_message_create import PreviewMessageCreate
from src.strategy.routes.dto.request.strategy_create import StrategyCreate
from src.strategy.routes.dto.response.preview_message_response import (
    PreviewMessageResponse,
)
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
    db: Session = Depends(get_db),
    get_strategy_service: GetStrategyUseCase = Depends(
        dependency=Provide[Container.get_strategy_service]
    ),
    user=Depends(get_permission_checker(required_permissions=[])),
) -> list[StrategyResponse]:
    return get_strategy_service.get_strategies(start_date, end_date, user, db=db)


@strategy_router.get("/strategies/{strategy_id}")
@inject
def read_strategy_object(
    strategy_id: str,
    db: Session = Depends(get_db),
    get_strategy_service: GetStrategyUseCase = Depends(
        dependency=Provide[Container.get_strategy_service]
    ),
    user=Depends(get_permission_checker(required_permissions=[])),
):
    return get_strategy_service.get_strategy_detail(strategy_id, db=db)


@strategy_router.post("/strategies")
@inject
def create_strategies(
    strategy_create: StrategyCreate,
    create_strategy_service: CreateStrategyUseCase = Depends(
        dependency=Provide[Container.create_strategy_service]
    ),
    db: Session = Depends(get_db),
    user=Depends(get_permission_checker(required_permissions=["subscription"])),
):
    result = create_strategy_service.create_strategy_object(strategy_create, user, db=db)
    return result


@strategy_router.delete("/strategies/{strategy_id}", status_code=status.HTTP_204_NO_CONTENT)
@inject
def delete_strategy(
    strategy_id: str,
    db: Session = Depends(get_db),
    delete_strategy_service: DeleteStrategyUseCase = Depends(
        Provide[Container.delete_strategy_service]
    ),
    user=Depends(get_permission_checker(required_permissions=["subscription"])),
):
    delete_strategy_service.exec(strategy_id, db=db)


@strategy_router.put("/strategies/{strategy_id}")
@inject
def update_strategy(
    strategy_id: str,
    strategy_update: StrategyCreate,
    db: Session = Depends(get_db),
    update_strategy_service: UpdateStrategyUseCase = Depends(
        Provide[Container.update_strategy_service]
    ),
    user=Depends(get_permission_checker(required_permissions=["subscription"])),
):
    update_strategy_service.exec(strategy_id, strategy_update, user, db=db)


@strategy_router.post("/themes/preview")
@inject
def get_preview(
    preview_message_create: PreviewMessageCreate,
    user=Depends(get_permission_checker(required_permissions=["subscription"])),
    db: Session = Depends(get_db),
    generate_message_service: GenerateMessageUsecase = Depends(
        dependency=Provide[Container.generate_message_service]
    ),
) -> PreviewMessageResponse:
    return generate_message_service.generate_preview_message(preview_message_create, user, db=db)
