from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from src.auth.utils.permission_checker import get_permission_checker
from src.common.pagination.pagination_base import PaginationBase
from src.common.pagination.pagination_response import PaginationResponse
from src.core.container import Container
from src.core.database import get_db_session
from src.products.routes.dto.request.product_link_update import ProductLinkUpdate
from src.products.routes.dto.request.product_update import ProductUpdate
from src.products.routes.dto.response.product_response import ProductResponse
from src.products.routes.port.base_product_service import BaseProductService

product_router = APIRouter(tags=["Products"])


@product_router.get("")
@inject
def get_all_products(
    based_on: str = "product_no",  # Enum으로 변경
    sort_by: str = "desc",  # Enum으로 변경
    current_page: int = 1,
    per_page: int = 10,
    user=Depends(get_permission_checker(required_permissions=[])),
    db: Session = Depends(get_db_session),
    product_service: BaseProductService = Depends(
        dependency=Provide[Container.product_service]
    ),
):
    product_response = product_service.get_all_products(
        based_on, sort_by, current_page, per_page, db=db
    )
    all_count = product_service.get_all_products_count(db)

    pagination = PaginationBase(
        total=all_count,
        per_page=per_page,
        current_page=current_page,
        total_page=(all_count // per_page) + 1,
    )

    return PaginationResponse(items=product_response, pagination=pagination)


@product_router.get("/{product_id}")
@inject
def get_product_detail(
    product_id: str,
    user=Depends(get_permission_checker(required_permissions=[])),
    db: Session = Depends(get_db_session),
    product_service: BaseProductService = Depends(
        dependency=Provide[Container.product_service]
    ),
) -> ProductResponse:
    return product_service.get_product_detail(product_id, db=db)


@product_router.patch("/{product_id}/links", status_code=status.HTTP_204_NO_CONTENT)
@inject
def update_product_link(
    product_id: str,
    product_link_update: ProductLinkUpdate,
    user=Depends(get_permission_checker(required_permissions=[])),
    db: Session = Depends(get_db_session),
    product_service: BaseProductService = Depends(
        dependency=Provide[Container.product_service]
    ),
):
    product_service.update_product_link(product_id, product_link_update, db=db)


@product_router.patch("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
@inject
def update_product(
    product_id: str,
    product_update: ProductUpdate,
    user=Depends(get_permission_checker(required_permissions=[])),
    db: Session = Depends(get_db_session),
    product_service: BaseProductService = Depends(
        dependency=Provide[Container.product_service]
    ),
):
    product_service.update(product_id, product_update, db=db)
