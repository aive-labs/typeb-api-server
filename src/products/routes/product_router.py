from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from src.auth.utils.permission_checker import get_permission_checker
from src.core.container import Container
from src.core.database import get_db_session
from src.products.routes.dto.response.product_response import ProductResponse
from src.products.routes.port.base_product_service import BaseProductService

product_router = APIRouter(tags=["Products"])


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
    return product_service.get_product_detail(product_id, db)
