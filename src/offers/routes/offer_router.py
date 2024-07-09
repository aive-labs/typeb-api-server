from typing import Optional

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from src.auth.utils.permission_checker import get_permission_checker
from src.common.pagination.pagination_response import PaginationResponse
from src.core.container import Container
from src.core.database import get_db_session
from src.offers.routes.dto.response.offer_response import OfferResponse
from src.offers.routes.port.get_offer_usecase import GetOfferUseCase

offer_router = APIRouter(
    tags=["Settings-Offers"],
)


@offer_router.get("/")
@inject
async def get_offer_object_list(
    based_on: str = "updated_at",  # Enum으로 변경
    sort_by: str = "desc",  # Enum으로 변경
    query: str | None = None,
    current_page: int = 1,
    per_page: int = 10,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    user=Depends(get_permission_checker(required_permissions=[])),
    db: Session = Depends(get_db_session),
    get_offer_service: GetOfferUseCase = Depends(Provide[Container.get_offer_service]),
) -> PaginationResponse[OfferResponse] | None:
    items = await get_offer_service.get_offers(
        based_on, sort_by, start_date, end_date, query, user, db=db
    )
    print("items")
    print(items)
    # items = items[(current_page - 1) * per_page: current_page * per_page]

    # pagination = PaginationBase(
    #     total=len(items),
    #     per_page=per_page,
    #     current_page=current_page,
    #     total_page=len(items) // per_page + 1,
    # )

    return None


# @offer_router.get("/{offer_key}")
# @inject
# def get_offer_detail(
#     offer_key: int,
#     user=Depends(get_permission_checker(required_permissions=[])),
#     get_offer_service: GetOfferUseCase = Depends(Provide[Container.get_offer_service]),
# ) -> OfferDetailResponse:
#     """오퍼 세부 내용을 조회하는 API"""
#     return get_offer_service.get_offer_detail(offer_key)
