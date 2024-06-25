from typing import Optional

from dependency_injector.wiring import Provide
from fastapi import APIRouter, Depends

from src.auth.utils.permission_checker import get_permission_checker
from src.common.pagination.pagination_base import PaginationBase
from src.common.pagination.pagination_response import PaginationResponse
from src.core.container import Container
from src.offers.routes.dto.offer_response import OfferResponse
from src.offers.routes.port.get_offer_usecase import GetOfferUseCase

offer_router = APIRouter(
    tags=["Settings-Offers"],
)


@offer_router.get("/")
async def get_offer_object_list(
    based_on: str = "updated_at",  # Enum으로 변경
    sort_by: str = "desc",  # Enum으로 변경
    query: str | None = None,
    current_page: int = 1,
    per_page: int = 10,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    user=Depends(get_permission_checker(required_permissions=[])),
    get_offer_service: GetOfferUseCase = Depends(Provide[Container.get_offer_service]),
) -> PaginationResponse[OfferResponse]:
    items = get_offer_service.get_offers(based_on, sort_by, start_date, end_date, query)

    items = items[(current_page - 1) * per_page : current_page * per_page]

    pagination = PaginationBase(
        total=len(items),
        per_page=per_page,
        current_page=current_page,
        total_page=len(items) // per_page + 1,
    )

    return PaginationResponse[OfferResponse](items=items, pagination=pagination)
