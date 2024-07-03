from typing import Optional

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from src.auth.utils.permission_checker import get_permission_checker
from src.core.container import Container
from src.core.database import get_db_session
from src.search.routes.dto.id_with_item_response import (
    IdWithItem,
    IdWithItemDescription,
)
from src.search.routes.dto.id_with_label_response import IdWithLabel
from src.search.routes.port.base_search_service import BaseSearchService
from src.strategy.enums.target_strategy import TargetStrategy

search_router = APIRouter(tags=["Search"])


@search_router.get("/audiences")
@inject
def get_strategies(
    target_strategy: Optional[TargetStrategy] = None,
    strategy_id: Optional[str] = None,
    keyword: Optional[str] = None,
    is_exclude: Optional[bool] = False,
    user=Depends(get_permission_checker(required_permissions=[])),
    search_service: BaseSearchService = Depends(
        dependency=Provide[Container.search_service]
    ),
) -> list[IdWithLabel]:
    if is_exclude is None:
        is_exclude = False

    if strategy_id:
        return search_service.search_audience_with_strategy_id(
            strategy_id, keyword, user, is_exclude
        )
    else:
        return search_service.search_audience_without_strategy_id(
            keyword, is_exclude, target_strategy.value if target_strategy else None
        )


@search_router.get("/offers")
@inject
def get_search_offers(
    strategy_id: Optional[str] = None,
    keyword: Optional[str] = None,
    user=Depends(get_permission_checker(required_permissions=[])),
    search_service: BaseSearchService = Depends(
        dependency=Provide[Container.search_service]
    ),
) -> list[IdWithLabel]:
    """드롭다운 오퍼 목록을 조회하는 API"""

    if strategy_id:
        return search_service.search_offers_search_of_sets(strategy_id, keyword, user)
    else:
        return search_service.search_offers(keyword, user)


@search_router.get("/recommend-products-models")
@inject
async def get_search_products(
    keyword: Optional[str] = None,
    user=Depends(get_permission_checker(required_permissions=[])),
    search_service: BaseSearchService = Depends(
        dependency=Provide[Container.search_service]
    ),
) -> list[IdWithItemDescription]:
    """드롭다운 추천모델 목록을 조회하는 API"""
    return search_service.search_recommend_products(keyword)


@search_router.get("/contents_tag")
@inject
async def get_contents_tag(
    keyword: Optional[str] = None,
    recsys_model_id: Optional[str] = None,
    db: Session = Depends(get_db_session),
    user=Depends(get_permission_checker(required_permissions=[])),
    search_service: BaseSearchService = Depends(
        dependency=Provide[Container.search_service]
    ),
) -> list[IdWithItem]:
    return search_service.search_contents_tag(keyword, recsys_model_id, db)
