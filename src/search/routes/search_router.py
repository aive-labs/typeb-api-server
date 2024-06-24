from typing import Optional

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends

from src.auth.utils.permission_checker import get_permission_checker
from src.core.container import Container
from src.search.routes.dto.id_with_label_response import IdWithLabel
from src.search.routes.port.base_search_service import BaseSearchService

search_router = APIRouter(tags=["Search"])


@search_router.get("/audience")
@inject
def get_strategies(
    audience_type_code: str,
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
            audience_type_code, keyword, is_exclude
        )
