from fastapi import APIRouter

creative_router = APIRouter(
    tags=["Creatives"],
)


@creative_router.get("/")
def get_img_creatives_list():
    pass


@creative_router.post("/")
def create_img_creatives():
    pass


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
