import math

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from src.auth.utils.permission_checker import get_permission_checker
from src.common.pagination.pagination_base import PaginationBase
from src.common.pagination.pagination_response import PaginationResponse
from src.main.container import Container
from src.main.db_dependency import get_db
from src.product.infra.dto.product_search_condition import ProductSearchCondition
from src.product.routes.dto.request.product_link_update import ProductLinkUpdate
from src.product.routes.dto.request.product_update import ProductUpdate
from src.product.routes.dto.response.product_response import ProductResponse
from src.product.routes.port.base_product_service import BaseProductService

product_router = APIRouter(tags=["Products"])


@product_router.get("")
@inject
def get_all_products(
    based_on: str = "product_no",  # Enum으로 변경
    sort_by: str = "desc",  # Enum으로 변경
    current_page: int = 1,
    per_page: int = 20,
    keyword: str | None = None,
    rep_nm: str | None = None,
    recommend_yn: str | None = None,
    sale_yn: str | None = None,
    user=Depends(get_permission_checker(required_permissions=[])),
    db: Session = Depends(get_db),
    product_service: BaseProductService = Depends(dependency=Provide[Container.product_service]),
):
    product_search_condition = ProductSearchCondition(
        keyword=keyword, rep_nm=rep_nm, recommend_yn=recommend_yn, sale_yn=sale_yn
    )

    product_response = product_service.get_all_products(
        based_on, sort_by, current_page, per_page, db=db, search_condition=product_search_condition
    )
    all_count = product_service.get_all_products_count(
        db=db, search_condition=product_search_condition
    )

    pagination = PaginationBase(
        total=all_count,
        per_page=per_page,
        current_page=current_page,
        total_page=math.ceil(all_count / per_page),
    )

    return PaginationResponse(items=product_response, pagination=pagination)


@product_router.get("/{product_id}")
@inject
def get_product_detail(
    product_id: str,
    user=Depends(get_permission_checker(required_permissions=[])),
    db: Session = Depends(get_db),
    product_service: BaseProductService = Depends(dependency=Provide[Container.product_service]),
) -> ProductResponse:
    product_response = product_service.get_product_detail(product_id, db=db)
    return product_response


@product_router.patch("/{product_id}/links", status_code=status.HTTP_204_NO_CONTENT)
@inject
def update_product_link(
    product_id: str,
    product_link_update: ProductLinkUpdate,
    user=Depends(get_permission_checker(required_permissions=["subscription"])),
    db: Session = Depends(get_db),
    product_service: BaseProductService = Depends(dependency=Provide[Container.product_service]),
):
    product_service.update_product_link(product_id, product_link_update, db=db)


@product_router.patch("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
@inject
def update_product(
    product_id: str,
    product_update: ProductUpdate,
    user=Depends(get_permission_checker(required_permissions=["subscription"])),
    db: Session = Depends(get_db),
    product_service: BaseProductService = Depends(dependency=Provide[Container.product_service]),
):
    product_service.update(product_id, product_update, db=db)
