import json
from typing import Optional, Union

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Body, Depends, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from src.auth.utils.permission_checker import get_permission_checker
from src.content.infra.dto.response.contents_menu_response import ContentsMenuResponse
from src.content.infra.dto.response.contents_response import ContentsResponse
from src.content.infra.dto.response.creative_recommend import CreativeRecommend
from src.content.routes.dto.request.contents_create import ContentsCreate
from src.content.routes.dto.request.contents_generate import ContentsGenerate
from src.content.routes.port.usecase.add_contents_usecase import AddContentsUseCase
from src.content.routes.port.usecase.delete_contents_usecase import (
    DeleteContentsUseCase,
)
from src.content.routes.port.usecase.get_contents_usecase import GetContentsUseCase
from src.content.routes.port.usecase.get_creative_recommendations_for_content_usecase import (
    GetCreativeRecommendationsForContentUseCase,
)
from src.content.routes.port.usecase.update_contents_usecase import (
    UpdateContentsUseCase,
)
from src.content.service.generate_contents_service import GenerateContentsService
from src.main.container import Container
from src.main.db_dependency import get_db

contents_router = APIRouter(
    tags=["Contents"],
)


@contents_router.get("/creatives/list")
@inject
def get_img_creatives_list(
    style_codes: Union[str, None] = None,
    subject: Union[str, None] = "",
    material1: Union[str, None] = "",
    material2: Union[str, None] = "",
    img_tag_nm: Union[str, None] = "",
    limit: int = 30,
    user=Depends(get_permission_checker(required_permissions=[])),
    db: Session = Depends(get_db),
    get_creative_recommendation: GetCreativeRecommendationsForContentUseCase = Depends(
        Provide[Container.get_creative_recommendation]
    ),
) -> list[CreativeRecommend]:
    return get_creative_recommendation.execute(
        db=db,
        style_codes=style_codes,
        subject=subject,
        material1=material1,
        material2=material2,
        img_tag_nm=img_tag_nm,
        limit=limit,
    )


@contents_router.post("")
@inject
def create_contents(
    content_create: ContentsCreate,
    user=Depends(get_permission_checker(required_permissions=["subscription"])),
    db: Session = Depends(get_db),
    add_contents_service: AddContentsUseCase = Depends(
        dependency=Provide[Container.add_contents_service]
    ),
):
    return add_contents_service.create_contents(content_create, user, db=db)


@contents_router.get("/menu/subject")
@inject
def get_contents_subject_list(
    style_yn: bool = True,
    user=Depends(get_permission_checker(required_permissions=[])),
    db: Session = Depends(get_db),
    get_contents_service: GetContentsUseCase = Depends(Provide[Container.get_contents_service]),
) -> list[ContentsMenuResponse]:
    return get_contents_service.get_subjects(style_yn, db=db)


@contents_router.get(path="/menu/with-subject")
@inject
def get_contents_menu_list(
    code: str,
    user=Depends(get_permission_checker(required_permissions=[])),
    db: Session = Depends(get_db),
    get_contents_service: GetContentsUseCase = Depends(Provide[Container.get_contents_service]),
) -> dict:
    return get_contents_service.get_with_subject(code, db=db)


@contents_router.get("")
@inject
def get_contents_list(
    based_on="updated_at",
    sort_by="desc",
    query: Optional[str] = None,
    current_page: int = 1,
    per_page: int = 10,
    user=Depends(get_permission_checker(required_permissions=[])),
    db: Session = Depends(get_db),
    get_contents_service: GetContentsUseCase = Depends(Provide[Container.get_contents_service]),
):
    pagination_result = get_contents_service.get_contents_list(
        db=db,
        based_on=based_on,
        sort_by=sort_by,
        query=query,
        current_page=current_page,
        per_page=per_page,
    )

    return pagination_result


@contents_router.get("/{contents_id}")
@inject
def get_contents(
    contents_id: int,
    user=Depends(get_permission_checker(required_permissions=[])),
    db: Session = Depends(get_db),
    get_contents_service: GetContentsUseCase = Depends(Provide[Container.get_contents_service]),
) -> ContentsResponse:
    return get_contents_service.get_contents(contents_id, db=db)


@contents_router.put("/{contents_id}")
@inject
def update_contents(
    contents_id: int,
    content_create: ContentsCreate,
    user=Depends(get_permission_checker(required_permissions=["subscription"])),
    db: Session = Depends(get_db),
    update_contents_service: UpdateContentsUseCase = Depends(
        Provide[Container.update_contents_service]
    ),
) -> ContentsResponse:
    return update_contents_service.exec(contents_id, content_create, user, db=db)


@contents_router.delete("/{contents_id}", status_code=status.HTTP_204_NO_CONTENT)
@inject
def delete_contents(
    contents_id: int,
    user=Depends(get_permission_checker(required_permissions=["subscription"])),
    db: Session = Depends(get_db),
    delete_contents_service: DeleteContentsUseCase = Depends(
        Provide[Container.delete_contents_service]
    ),
):
    delete_contents_service.exec(contents_id, db=db)


@contents_router.post("/generate")
@inject
async def generate_contents(
    contents_generate_req: str = Body(...),
    db: Session = Depends(get_db),
    user=Depends(get_permission_checker(required_permissions=["subscription"])),
    generate_contents_service: GenerateContentsService = Depends(
        Provide[Container.generate_contents_service]
    ),
) -> StreamingResponse:
    """Generate content from given request.
    참고: 스트리밍 리스폰스를 사용할 때는, string으로 받아서 json.loads를 해야함.
    """
    generate_req = json.loads(contents_generate_req)
    generation_obj = ContentsGenerate(**generate_req)
    return StreamingResponse(
        generate_contents_service.exec(generation_obj, db, user),
        media_type="text/event-stream",
    )
