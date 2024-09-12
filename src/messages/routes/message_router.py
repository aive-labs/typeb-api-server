import json

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, HTTPException, Request, UploadFile, status
from fastapi.params import File, Form
from sqlalchemy.orm import Session

from src.auth.utils.permission_checker import get_permission_checker
from src.core.container import Container
from src.core.db_dependency import get_db, get_db_for_with_mall_id
from src.messages.routes.dto.ppurio_message_result import PpurioMessageResult
from src.messages.routes.dto.request.kakao_carousel_card_request import (
    KakaoCarouselCardRequest,
    KakaoCarouselLinkButtonsRequest,
)
from src.messages.routes.dto.request.kakao_carousel_more_link_request import (
    KakaoCarouselMoreLinkRequest,
)
from src.messages.routes.dto.response.kakao_carousel_card_response import (
    KakaoCarouselCardResponse,
)
from src.messages.routes.port.create_carousel_card_usecase import (
    CreateCarouselCardUseCase,
)
from src.messages.routes.port.create_carousel_more_link_usecase import (
    CreateCarouselMoreLinkUseCase,
)
from src.messages.routes.port.delete_carousel_card_usecase import (
    DeleteCarouselCardUseCase,
)
from src.messages.service.message_service import MessageService

message_router = APIRouter(
    tags=["Message"],
)

# TODO: 허용할 IP 목록
ALLOWED_IPS = {"123.123.123.123", "124.124.124.124"}


# 요청 IP를 프린트하는 의존성
def get_client_ip(request: Request):
    client = request.client
    if client is None:
        return "unknown ip"
    return client.host


# IP 검증 의존성 정의
def verify_ip(request: Request):
    """의존성 사용"""
    client = request.client
    if client is None:
        return "unknown ip"
    client_ip = client.host

    if client_ip not in ALLOWED_IPS:
        raise HTTPException(status_code=403, detail="Forbidden")
    return client_ip


@message_router.post("/result")
@inject
def get_message_result_from_ppurio(
    ppurio_message_result: PpurioMessageResult,
    client_ip: str = Depends(get_client_ip),
    message_service: MessageService = Depends(Provide[Container.message_service]),
):
    refkey = ppurio_message_result.REFKEY
    if refkey is None:
        raise HTTPException(
            status_code=503, detail={"messages": "REFKEY가 존재하지 않는 메시지 입니다."}
        )

    # == 으로 구분함
    mall_id = refkey.split("==")[0]
    db = get_db_for_with_mall_id(mall_id)

    print(f"Bizppurio result log from ip: {client_ip}")
    message_service.save_message_result(ppurio_message_result, db=db)

    db.close()


def parse_carousel_card(
    carousel_card: str = Form(...), carousel_button_links: str = Form(...)
) -> KakaoCarouselCardRequest:
    card_data = json.loads(carousel_card)
    button_links_data = json.loads(carousel_button_links)

    card_data["carousel_button_links"] = [
        KakaoCarouselLinkButtonsRequest(**link) for link in button_links_data
    ]

    return KakaoCarouselCardRequest(**card_data)


@message_router.post("/kakao-carousel")
@inject
async def add_kakao_carousel_card(
    file: UploadFile = File(...),
    carousel_card: KakaoCarouselCardRequest = Depends(parse_carousel_card),
    db: Session = Depends(get_db),
    user=Depends(get_permission_checker(required_permissions=["subscription"])),
    create_carousel_card: CreateCarouselCardUseCase = Depends(
        Provide[Container.create_carousel_card]
    ),
) -> KakaoCarouselCardResponse:
    return await create_carousel_card.create_carousel_card(file, carousel_card, user, db)


@message_router.delete("/kakao-carousel/{carousel_card_id}")
@inject
def delete_kakao_carousel_card(
    carousel_card_id: int,
    db: Session = Depends(get_db),
    user=Depends(get_permission_checker(required_permissions=["subscription"])),
    delete_carousel_card: DeleteCarouselCardUseCase = Depends(
        Provide[Container.delete_carousel_card]
    ),
):
    delete_carousel_card.exec(carousel_card_id, db=db)


@message_router.post(
    "/{set_group_msg_seq}/kakao-carousel-more-link", status_code=status.HTTP_201_CREATED
)
@inject
def create_kakao_carousel_more_link(
    set_group_msg_seq: int,
    carousel_more_link_request: KakaoCarouselMoreLinkRequest,
    db: Session = Depends(get_db),
    user=Depends(get_permission_checker(required_permissions=["subscription"])),
    create_carousel_more_link: CreateCarouselMoreLinkUseCase = Depends(
        Provide[Container.create_carousel_more_link]
    ),
):
    create_carousel_more_link.exec(set_group_msg_seq, carousel_more_link_request, user, db=db)
