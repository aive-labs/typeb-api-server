from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, HTTPException, Request

from src.core.container import Container
from src.messages.routes.dto.ppurio_message_result import PpurioMessageResult
from src.messages.service.message_service import MessageService

message_router = APIRouter(
    tags=["Message"],
)


# 요청 IP를 프린트하는 의존성
def get_client_ip(request: Request):
    client = request.client
    if client is None:
        return "unknown ip"
    return client.host


# TODO: 허용할 IP 목록
ALLOWED_IPS = {"123.123.123.123", "124.124.124.124"}


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
    print(f"Bizppurio result log from ip: {client_ip}")
    message_service.save_message_result(ppurio_message_result)
