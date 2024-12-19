from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from src.auth.routes.dto.request.kakao_channel_request import KakaoChannelRequest
from src.auth.routes.dto.request.message_sender_request import MessageSenderRequest
from src.auth.routes.dto.request.onboarding_request import OnboardingRequest
from src.auth.routes.dto.response.kakao_channel_response import KakaoChannelResponse
from src.auth.routes.dto.response.message_sender_response import MessageSenderResponse
from src.auth.routes.dto.response.onboarding_response import OnboardingResponse
from src.auth.routes.port.base_onboarding_service import BaseOnboardingService
from src.auth.utils.permission_checker import get_permission_checker
from src.main.container import Container
from src.main.db_dependency import get_db

onboarding_router = APIRouter(
    tags=["Onboarding"],
)


@onboarding_router.get("/{mall_id}")
@inject
def get_onboarding_status(
    mall_id: str,
    user=Depends(get_permission_checker(required_permissions=[])),
    db: Session = Depends(get_db),
    onboarding_service: BaseOnboardingService = Depends(Provide[Container.onboarding_service]),
) -> OnboardingResponse | None:
    return onboarding_service.get_onboarding_status(mall_id=mall_id, user=user, db=db)


@onboarding_router.patch("/{mall_id}")
@inject
def update_onboarding_status(
    mall_id: str,
    onboarding_request: OnboardingRequest,
    user=Depends(get_permission_checker(required_permissions=[])),
    db: Session = Depends(get_db),
    onboarding_service: BaseOnboardingService = Depends(Provide[Container.onboarding_service]),
) -> OnboardingResponse:
    return onboarding_service.update_onboarding_status(
        mall_id=mall_id, status=onboarding_request.onboarding_status, db=db
    )


@onboarding_router.post("/{mall_id}/message", status_code=status.HTTP_201_CREATED)
@inject
def register_message_sender(
    mall_id: str,
    message_sender_request: MessageSenderRequest,
    user=Depends(get_permission_checker(required_permissions=[])),
    db: Session = Depends(get_db),
    onboarding_service: BaseOnboardingService = Depends(Provide[Container.onboarding_service]),
):
    onboarding_service.register_message_sender(mall_id, message_sender_request, db=db)


@onboarding_router.put("/{mall_id}/message", status_code=status.HTTP_204_NO_CONTENT)
@inject
def updates_message_sender(
    mall_id: str,
    message_sender_request: MessageSenderRequest,
    user=Depends(get_permission_checker(required_permissions=[])),
    db: Session = Depends(get_db),
    onboarding_service: BaseOnboardingService = Depends(Provide[Container.onboarding_service]),
):
    onboarding_service.update_message_sender(mall_id, message_sender_request, db=db)


@onboarding_router.get("/{mall_id}/message")
@inject
def get_message_sender(
    mall_id: str,
    user=Depends(get_permission_checker(required_permissions=[])),
    db: Session = Depends(get_db),
    onboarding_service: BaseOnboardingService = Depends(Provide[Container.onboarding_service]),
) -> MessageSenderResponse | None:
    return onboarding_service.get_message_sender(mall_id, db=db)


@onboarding_router.post("/{mall_id}/kakao", status_code=status.HTTP_201_CREATED)
@inject
def register_kakao_channel(
    mall_id: str,
    kakao_channel_request: KakaoChannelRequest,
    user=Depends(get_permission_checker(required_permissions=[])),
    db: Session = Depends(get_db),
    onboarding_service: BaseOnboardingService = Depends(Provide[Container.onboarding_service]),
):
    onboarding_service.register_kakao_channel(mall_id, kakao_channel_request, db=db)


@onboarding_router.put("/{mall_id}/kakao", status_code=status.HTTP_201_CREATED)
@inject
def update_kakao_channel(
    mall_id: str,
    kakao_channel_request: KakaoChannelRequest,
    user=Depends(get_permission_checker(required_permissions=[])),
    db: Session = Depends(get_db),
    onboarding_service: BaseOnboardingService = Depends(Provide[Container.onboarding_service]),
):
    onboarding_service.update_kakao_channel(mall_id, kakao_channel_request, db=db)


@onboarding_router.get("/{mall_id}/kakao")
@inject
def get_kakao_channel(
    mall_id: str,
    user=Depends(get_permission_checker(required_permissions=[])),
    db: Session = Depends(get_db),
    onboarding_service: BaseOnboardingService = Depends(Provide[Container.onboarding_service]),
) -> KakaoChannelResponse | None:
    return onboarding_service.get_kakao_channel(mall_id=mall_id, db=db)
