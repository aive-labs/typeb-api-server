from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, Request

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


@message_router.post("/message/result")
@inject
def get_message_result_from_ppurio(
    ppurio_message_result: PpurioMessageResult,
    client_ip: str = Depends(get_client_ip),
    message_service: MessageService = Depends(Provide[Container.message_service]),
):
    print(f"Bizppurio result log from ip: {client_ip}")
    message_service.save_message_result(ppurio_message_result)
