from dependency_injector.wiring import inject
from fastapi import APIRouter

contents_router = APIRouter(
    tags=["Contents"],
)


@contents_router.post("/generate")
@inject  # UserService 주입
def generate_contents():
    pass


@contents_router.get("/menu/subject")
def get_contents_subject_list():
    pass


@contents_router.get(path="/menu/with-subject")
def get_contents_menu_list():
    pass


@contents_router.post("/")
def create_contents():
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
