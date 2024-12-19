from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from src.auth.utils.permission_checker import get_permission_checker
from src.common.pagination.pagination_response import PaginationResponse
from src.content.domain.creatives import Creatives
from src.content.enums.image_asset_type import ImageAssetTypeEnum
from src.content.infra.dto.response.s3_presigned_response import S3PresignedResponse
from src.content.routes.dto.request.contents_create import StyleObject
from src.content.routes.dto.request.creatives_create import CreativeCreate
from src.content.routes.dto.request.s3_presigned_url_request import (
    S3PresignedUrlRequest,
)
from src.content.routes.dto.response.creative_base import CreativeBase
from src.content.routes.port.usecase.add_creatives_usecase import AddCreativesUseCase
from src.content.routes.port.usecase.delete_creatives_usecase import (
    DeleteCreativesUseCase,
)
from src.content.routes.port.usecase.get_creatives_usecase import GetCreativesUseCase
from src.content.routes.port.usecase.update_creatives_usecase import (
    UpdateCreativesUseCase,
)
from src.core.container import Container
from src.core.db_dependency import get_db

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
    current_page: int = 1,
    per_page: int = 10,
    user=Depends(get_permission_checker(required_permissions=[])),
    db: Session = Depends(get_db),
    get_creatives_service: GetCreativesUseCase = Depends(Provide[Container.get_creatives_service]),
) -> PaginationResponse[CreativeBase]:
    pagination_result = get_creatives_service.get_creatives(
        db=db,
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
    asset_data: S3PresignedUrlRequest,
    user=Depends(get_permission_checker(required_permissions=["subscription"])),
    db: Session = Depends(get_db),
    add_creatives_service: AddCreativesUseCase = Depends(
        dependency=Provide[Container.add_creatives_service]
    ),
) -> list[S3PresignedResponse]:
    return add_creatives_service.generate_s3_url(asset_data, user, db=db)


@creatives_router.post("", status_code=status.HTTP_201_CREATED)
@inject
def create_img_creatives(
    asset_data: CreativeCreate,
    user=Depends(get_permission_checker(required_permissions=["subscription"])),
    db: Session = Depends(get_db),
    add_creatives_service: AddCreativesUseCase = Depends(
        dependency=Provide[Container.add_creatives_service]
    ),
) -> list[Creatives]:
    return add_creatives_service.create_creatives(asset_data=asset_data, user=user, db=db)


@creatives_router.delete("/{creative_id}", status_code=status.HTTP_204_NO_CONTENT)
@inject
def delete_img_creatives(
    creative_id: int,
    user=Depends(get_permission_checker(required_permissions=["subscription"])),
    db: Session = Depends(get_db),
    delete_creatives_service: DeleteCreativesUseCase = Depends(
        Provide[Container.delete_creatives_service]
    ),
):
    delete_creatives_service.exec(creative_id, db=db)


@creatives_router.put("/{creative_id}", status_code=status.HTTP_200_OK)
@inject
def update_img_creatives(
    creative_id: int,
    creative_update: CreativeCreate,
    user=Depends(get_permission_checker(required_permissions=["subscription"])),
    db: Session = Depends(get_db),
    update_creatives_service: UpdateCreativesUseCase = Depends(
        dependency=Provide[Container.update_creatives_service]
    ),
) -> Creatives:
    if len(creative_update.files) > 1:
        raise HTTPException(
            status_code=400,
            detail={
                "code": "image_asset/update",
                "message": "한번에 하나의 이미지만 수정할 수 있습니다.",
            },
        )

    return update_creatives_service.update_creative(creative_id, creative_update, user, db=db)


@creatives_router.get("/{creative_id}")
@inject
def get_img_creatives(
    creative_id: int,
    user=Depends(get_permission_checker(required_permissions=[])),
    db: Session = Depends(get_db),
    get_creatives_service: GetCreativesUseCase = Depends(Provide[Container.get_creatives_service]),
):
    """이미지 에셋을 조회하는 API"""
    return get_creatives_service.get_creatives_detail(creative_id, db=db)


@creatives_router.get("/style/list")
@inject
def get_style_list(
    user=Depends(get_permission_checker(required_permissions=[])),
    db: Session = Depends(get_db),
    get_creatives_service: GetCreativesUseCase = Depends(Provide[Container.get_creatives_service]),
) -> list[StyleObject]:
    return get_creatives_service.get_style_list(db=db)
