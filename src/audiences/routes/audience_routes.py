
from fastapi import APIRouter, Depends

from src.audiences.routes.dto.response.audiences import AudienceResponse
from src.auth.utils.permission_checker import get_permission_checker

audience_router = APIRouter(tags=["audience"])


@audience_router.get("/audiences", response_model=AudienceResponse)
def get_audiences(
    is_exclude: bool | None = None, user=Depends(get_permission_checker)
):
    pass
