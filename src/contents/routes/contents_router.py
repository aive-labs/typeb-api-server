from typing import Optional

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends

from src.auth.utils.permission_checker import get_permission_checker
from src.contents.infra.dto.response.contents_menu_response import ContentsMenuResponse
from src.contents.routes.port.usecase.get_contents_usecase import GetContentsUseCase
from src.core.container import Container

contents_router = APIRouter(
    tags=["Contents"],
)


@contents_router.post("/generate")
@inject  # UserService 주입
def generate_contents():
    pass


@contents_router.get("/creatives/list")
def get_img_creatives_list():
    pass


# @contents_router.post("/")
# @inject
# def create_contents(
#     content_create: ContentsCreate,
#     files: UploadFile | None = None,
#     user=Depends(get_permission_checker),
#     add_contents_service: AddContentsUseCase = Depends(
#         dependency=Provide[Container.add_contents_service]
#     ),
# ):
#     add_contents_service.create_contents(content_create, user, files)


@contents_router.get("/menu/subject")
@inject
def get_contents_subject_list(
    style_yn: bool = True,
    user=Depends(get_permission_checker(required_permissions=[])),
    get_contents_service: GetContentsUseCase = Depends(
        Provide[Container.get_contents_service]
    ),
) -> list[ContentsMenuResponse]:
    return get_contents_service.get_subjects(style_yn)


@contents_router.get(path="/menu/with-subject")
@inject
def get_contents_menu_list(
    code: str,
    user=Depends(get_permission_checker(required_permissions=[])),
    get_contents_service: GetContentsUseCase = Depends(
        Provide[Container.get_contents_service]
    ),
) -> dict:
    return get_contents_service.get_with_subject(code)


@contents_router.get("/")
@inject
def get_contents_list(
    based_on="updated_at",
    sort_by="desc",
    query: Optional[str] = None,
    current_page: int = 1,
    per_page: int = 10,
    user=Depends(get_permission_checker(required_permissions=[])),
    get_contents_service: GetContentsUseCase = Depends(
        Provide[Container.get_contents_service]
    ),
):
    pagination_result = get_contents_service.get_contents_list(
        based_on=based_on,
        sort_by=sort_by,
        query=query,
        current_page=current_page,
        per_page=per_page,
    )

    return pagination_result


@contents_router.get("/{contents_id}")
@inject
def get_contents():
    pass


@contents_router.put("/{contents_id}")
@inject
def update_contents():
    pass


@contents_router.delete("/{contents_id}")
@inject
def delete_contents():
    pass
