from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, UploadFile, status

from src.auth.utils.permission_checker import get_permission_checker
from src.common.pagination.pagination_response import PaginationResponse
from src.contents.enums.image_asset_type import ImageAssetTypeEnum
from src.contents.routes.dto.request.creatives_create import CreativeCreate
from src.contents.routes.dto.response.creative_base import CreativeBase
from src.contents.routes.port.usecase.add_creatives_usecase import AddCreativesUseCase
from src.contents.routes.port.usecase.get_creatives_usecase import GetCreativesUseCase
from src.core.container import Container

creative_router = APIRouter(
    tags=["Creatives"],
)


@creative_router.get(
    "/",
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
        based_on,
        sort_by,
        asset_type,
        query,
        current_page,
        per_page,
    )
    return pagination_result


@creative_router.post("/", status_code=status.HTTP_201_CREATED)
@inject
async def create_img_creatives(
    asset_data: CreativeCreate,
    files: list[UploadFile],
    user=Depends(get_permission_checker),
    add_creatives_service: AddCreativesUseCase = Depends(
        dependency=Provide[Container.add_creatives_service]
    ),
):
    await add_creatives_service.upload_image(asset_data=asset_data, files=files)


@creative_router.get("/creatives/list")
def get_creatives_ilst():
    pass


@creative_router.delete("/{creative_id}")
def delete_img_creatives():
    pass


@creative_router.put("/{creative_id}")
async def update_img_creatives():
    pass


@creative_router.get("/{creative_id}")
def get_img_creatives():
    """이미지 에셋을 조회하는 API"""
    pass


@creative_router.get("/style/list")
def get_style_list():
    """스타일 목록을 조회하는 API"""
    pass
