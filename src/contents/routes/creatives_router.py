from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, status

from src.auth.utils.permission_checker import get_permission_checker
from src.common.pagination.pagination_response import PaginationResponse
from src.contents.domain.creatives import Creatives
from src.contents.enums.image_asset_type import ImageAssetTypeEnum
from src.contents.infra.dto.response.s3_presigned_response import S3PresignedResponse
from src.contents.routes.dto.request.contents_create import StyleObjectBase
from src.contents.routes.dto.request.creatives_create import CreativeCreate
from src.contents.routes.dto.response.creative_base import CreativeBase
from src.contents.routes.port.usecase.add_creatives_usecase import AddCreativesUseCase
from src.contents.routes.port.usecase.delete_creatives_usecase import (
    DeleteCreativesUseCase,
)
from src.contents.routes.port.usecase.get_creatives_usecase import GetCreativesUseCase
from src.core.container import Container

creatives_router = APIRouter(
    tags=["Creatives"],
)


@creatives_router.get(
    "",
    response_model=PaginationResponse,
    status_code=status.HTTP_200_OK,
)
@inject
def get_img_creatives_list(
    asset_type: ImageAssetTypeEnum | None = None,
    based_on: str = "updated_at",  # Enum으로 변경
    sort_by: str = "desc",  # Enum으로 변경
    query: str | None = None,
    current_page: int | None = 1,
    per_page: int | None = 10,
    get_creatives_service: GetCreativesUseCase = Depends(
        Provide[Container.get_creatives_service]
    ),
) -> PaginationResponse[CreativeBase]:
    pagination_result = get_creatives_service.get_creatives(
        based_on=based_on,
        sort_by=sort_by,
        asset_type=asset_type,
        query=query,
        current_page=current_page,
        per_page=per_page,
    )
    return pagination_result


@creatives_router.post("/upload", status_code=status.HTTP_200_OK)
@inject
def generate_s3_presigned_url(
    asset_data: CreativeCreate,
    user=Depends(get_permission_checker(required_permissions=[])),
    add_creatives_service: AddCreativesUseCase = Depends(
        dependency=Provide[Container.add_creatives_service]
    ),
) -> list[S3PresignedResponse]:
    return add_creatives_service.generate_s3_url(asset_data, user)


@creatives_router.post("", status_code=status.HTTP_201_CREATED)
@inject
def create_img_creatives(
    asset_data: CreativeCreate,
    user=Depends(get_permission_checker(required_permissions=[])),
    add_creatives_service: AddCreativesUseCase = Depends(
        dependency=Provide[Container.add_creatives_service]
    ),
) -> list[Creatives]:
    return add_creatives_service.create_creatives(asset_data=asset_data, user=user)


@creatives_router.delete("/{creative_id}", status_code=status.HTTP_204_NO_CONTENT)
@inject
def delete_img_creatives(
    creative_id: int,
    user=Depends(get_permission_checker(required_permissions=[])),
    delete_creatives_service: DeleteCreativesUseCase = Depends(
        Provide[Container.delete_creatives_service]
    ),
):
    delete_creatives_service.delete_creative(creative_id)


@creatives_router.put("/{creative_id}")
@inject
def update_img_creatives(
    creative_id: str,
    creative_update: CreativeCreate,
    user=Depends(get_permission_checker(required_permissions=[])),
    add_creatives_service: AddCreativesUseCase = Depends(
        dependency=Provide[Container.add_creatives_service]
    ),
):
    pass


@creatives_router.get("/{creative_id}")
@inject
def get_img_creatives(
    creative_id: int,
    user=Depends(get_permission_checker(required_permissions=[])),
    get_creatives_service: GetCreativesUseCase = Depends(
        Provide[Container.get_creatives_service]
    ),
):
    """이미지 에셋을 조회하는 API"""
    return get_creatives_service.get_creatives_detail(creative_id)


@creatives_router.get("/style/list")
@inject
def get_style_list(
    user=Depends(get_permission_checker(required_permissions=[])),
    get_creatives_service: GetCreativesUseCase = Depends(
        Provide[Container.get_creatives_service]
    ),
) -> list[StyleObjectBase]:
    return get_creatives_service.get_style_list()
