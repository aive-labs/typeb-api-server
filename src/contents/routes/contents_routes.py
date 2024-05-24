
from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, UploadFile

from src.auth.utils.permission_checker import get_permission_checker
from src.contents.routes.dto.request.contents_create import ContentsCreate
from src.contents.routes.port.usecase.add_contents_usecase import AddContentsUseCase
from src.core.container import Container

contents_router = APIRouter(
    tags=["Contents"],
)


@contents_router.post("/generate")
@inject  # UserService 주입
def generate_contents():
    pass


@contents_router.post("/")
@inject
def create_contents(
    content_create: ContentsCreate,
    files: UploadFile | None = None,
    user=Depends(get_permission_checker),
    add_contents_service: AddContentsUseCase = Depends(
        dependency=Provide[Container.add_contents_service]
    ),
):
    add_contents_service.create_contents(content_create, user, files)


@contents_router.get("/menu/subject")
def get_contents_subject_list():
    pass


@contents_router.get(path="/menu/with-subject")
def get_contents_menu_list():
    pass


@contents_router.get("/")
def get_contents_list():
    pass


@contents_router.get("/{contents_id}")
def get_contents():
    pass


@contents_router.put("/{contents_id}")
def update_contents():
    pass


@contents_router.delete("/{contents_id}")
def delete_contents():
    pass
