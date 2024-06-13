from typing import Optional, Union

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends

from src.auth.utils.permission_checker import get_permission_checker
from src.contents.infra.dto.response.contents_menu_response import ContentsMenuResponse
from src.contents.infra.dto.response.creative_recommend import CreativeRecommend
from src.contents.routes.dto.request.contents_create import ContentsCreate
from src.contents.routes.port.usecase.add_contents_usecase import AddContentsUseCase
from src.contents.routes.port.usecase.get_contents_usecase import GetContentsUseCase
from src.contents.routes.port.usecase.get_creative_recommendations_for_content_usecase import (
    GetCreativeRecommendationsForContentUseCase,
)
from src.core.container import Container

contents_router = APIRouter(
    tags=["Contents"],
)


# @contents_router.post("/generate")
# @inject  # UserService 주입
# def generate_contents(
#     contents_generate: ContentsGenerate,
#     user=Depends(get_permission_checker(required_permissions=[])),
# ):
#     """
#     문장 메시지 생성 API
#     템플릿 : subject/material1,2 무관
#     subject - 상품존재 RAG
#     subject - 상품X
#     트래킹코스 소개-등산용품이야기(sn1~sn7) RAG
#     상품관리 TIP : DB데이터+GPT
#     자유주제 : GPT
#     """
#
#     selected_template = contents_template_prompts[contents_generate.template]
#     chain = StreamingConversationChain(
#         openai_api_key=get_env_variable("openai_api_key"),
#     )
#
#     return StreamingResponse(
#         chain.generate_response(selected_template, message, **kwargs_dict),
#         media_type="text/event-stream"
#     )


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
    get_creative_recommendation: GetCreativeRecommendationsForContentUseCase = Depends(
        Provide[Container.get_creative_recommendation]
    ),
) -> list[CreativeRecommend]:
    return get_creative_recommendation.execute(
        style_codes, subject, material1, material2, img_tag_nm, limit
    )


@contents_router.post("/")
@inject
def create_contents(
    content_create: ContentsCreate,
    user=Depends(get_permission_checker),
    add_contents_service: AddContentsUseCase = Depends(
        dependency=Provide[Container.add_contents_service]
    ),
):
    add_contents_service.create_contents(content_create, user)


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
