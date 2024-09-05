from typing import Optional

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from src.auth.utils.permission_checker import get_permission_checker
from src.core.container import Container
from src.core.db_dependency import get_db
from src.search.routes.dto.id_with_item_response import (
    IdWithItem,
    IdWithItemDescription,
)
from src.search.routes.dto.id_with_label_response import IdWithLabel
from src.search.routes.dto.reviewer_response import ReviewerResponse
from src.search.routes.dto.send_user_response import SendUserResponse
from src.search.routes.dto.strategy_search_response import StrategySearchResponse
from src.search.routes.port.base_search_service import BaseSearchService
from src.strategy.enums.target_strategy import TargetStrategy

search_router = APIRouter(tags=["Search"])


@search_router.get("/audiences")
@inject
def get_strategies(
    target_strategy: Optional[TargetStrategy] = None,
    strategy_id: Optional[str] = None,
    strategy_theme_id: Optional[str] = None,
    keyword: Optional[str] = None,
    is_exclude: Optional[bool] = False,
    user=Depends(get_permission_checker(required_permissions=[])),
    db: Session = Depends(get_db),
    search_service: BaseSearchService = Depends(dependency=Provide[Container.search_service]),
) -> list[IdWithLabel]:
    if is_exclude is None:
        is_exclude = False

    if strategy_id:
        return search_service.search_audience_with_strategy_id(
            strategy_id, keyword, user, db, is_exclude, strategy_theme_id
        )
    else:
        return search_service.search_audience_without_strategy_id(
            keyword, db, is_exclude, target_strategy.value if target_strategy else None
        )


@search_router.get("/offers")
@inject
def get_search_offers(
    strategy_id: Optional[str] = None,
    keyword: Optional[str] = None,
    strategy_theme_id: Optional[str] = None,
    user=Depends(get_permission_checker(required_permissions=[])),
    db: Session = Depends(get_db),
    search_service: BaseSearchService = Depends(dependency=Provide[Container.search_service]),
) -> list[IdWithLabel]:
    """드롭다운 오퍼 목록을 조회하는 API"""

    if strategy_id:
        return search_service.search_offers_search_of_sets(
            strategy_id, keyword, user, db=db, strategy_theme_id=strategy_theme_id
        )
    else:
        return search_service.search_offers(keyword, user, db=db)


@search_router.get("/recommend-products-models")
@inject
async def get_search_products(
    keyword: Optional[str] = None,
    user=Depends(get_permission_checker(required_permissions=[])),
    db: Session = Depends(get_db),
    search_service: BaseSearchService = Depends(dependency=Provide[Container.search_service]),
) -> list[IdWithItemDescription]:
    """드롭다운 추천모델 목록을 조회하는 API"""
    return search_service.search_recommend_products(keyword, db=db)


@search_router.get("/contents")
@inject
def search_contents(
    strategy_theme_id: int,
    keyword: Optional[str] = None,
    db: Session = Depends(get_db),
    user=Depends(get_permission_checker(required_permissions=[])),
    search_service: BaseSearchService = Depends(dependency=Provide[Container.search_service]),
) -> list[IdWithItem]:
    return search_service.search_contents(strategy_theme_id, db=db, keyword=keyword)


@search_router.get("/contents_tag")
@inject
def get_contents_tag(
    keyword: Optional[str] = None,
    recsys_model_id: Optional[str] = None,
    db: Session = Depends(get_db),
    user=Depends(get_permission_checker(required_permissions=[])),
    search_service: BaseSearchService = Depends(dependency=Provide[Container.search_service]),
) -> list[IdWithItem]:
    return search_service.search_contents_tag(keyword, recsys_model_id, db=db)


@search_router.get("/campaigns")
@inject
def search_campaign(
    keyword: Optional[str] = None,
    db: Session = Depends(get_db),
    user=Depends(get_permission_checker(required_permissions=[])),
    search_service: BaseSearchService = Depends(dependency=Provide[Container.search_service]),
) -> list[IdWithItem]:
    """
    드롭다운 캠페인 목록을 조회하는 API

    당일 기준 직전 2주내 시작 또는 종료된 캠페인 &
    운영중 또는 종료, 기간만료된 캠페인
    """
    return search_service.search_campaign(keyword, db=db)


@search_router.get("/rep-nms")
@inject
def search_rep_nms(
    product_id: Optional[str] = None,
    db: Session = Depends(get_db),
    user=Depends(get_permission_checker(required_permissions=[])),
    search_service: BaseSearchService = Depends(dependency=Provide[Container.search_service]),
) -> list[str]:
    rep_nm_list = search_service.search_rep_nms(product_id, db=db)
    return rep_nm_list


@search_router.get("/strategies")
@inject
def search_strategies(
    campaign_type_code: str,
    keyword: Optional[str] = None,
    db: Session = Depends(get_db),
    user=Depends(get_permission_checker(required_permissions=[])),
    search_service: BaseSearchService = Depends(dependency=Provide[Container.search_service]),
) -> list[StrategySearchResponse]:
    return search_service.search_strategies(campaign_type_code, keyword, db=db)


@search_router.get("/themes")
@inject
def search_strategy_themes(
    strategy_id: str,
    db: Session = Depends(get_db),
    user=Depends(get_permission_checker(required_permissions=[])),
    search_service: BaseSearchService = Depends(dependency=Provide[Container.search_service]),
) -> list[IdWithItem]:
    return search_service.search_strategy_themes(strategy_id, db=db)


@search_router.get("/send-users")
@inject
def search_send_users(
    keyword: Optional[str] = None,
    db: Session = Depends(get_db),
    user=Depends(get_permission_checker(required_permissions=[])),
    search_service: BaseSearchService = Depends(dependency=Provide[Container.search_service]),
) -> list[SendUserResponse]:
    return search_service.search_send_users(db=db, keyword=keyword)


@search_router.get("/review-users")
@inject
def search_reviewers(
    keyword: Optional[str] = None,
    db: Session = Depends(get_db),
    user=Depends(get_permission_checker(required_permissions=[])),
    search_service: BaseSearchService = Depends(dependency=Provide[Container.search_service]),
) -> list[ReviewerResponse]:
    return search_service.search_reviewer(user=user, db=db, keyword=keyword)
