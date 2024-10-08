from typing import Optional

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from src.auth.routes.port.base_onboarding_service import BaseOnboardingService
from src.auth.utils.permission_checker import get_permission_checker
from src.common.enums.campaign_media import CampaignMedia
from src.core.container import Container
from src.core.db_dependency import get_db
from src.message_template.domain.message_template import MessageTemplate
from src.message_template.routes.dto.request.message_template_create import (
    TemplateCreate,
)
from src.message_template.routes.dto.request.message_template_update import (
    TemplateUpdate,
)
from src.message_template.routes.dto.response.opt_out_phone_number_response import (
    OptOutPhoneNumberResponse,
)
from src.message_template.service.create_message_template_service import (
    CreateMessageTemplateService,
)
from src.message_template.service.delete_message_template_service import (
    DeleteMessageTemplateService,
)
from src.message_template.service.get_message_template_service import (
    GetMessageTemplateService,
)
from src.message_template.service.update_message_template_service import (
    UpdateMessageTemplateService,
)

message_template_router = APIRouter(
    tags=["Settings-message-templates"],
)


@message_template_router.post("", status_code=status.HTTP_201_CREATED)
@inject
def create_message_template(
    template_create: TemplateCreate,
    user=Depends(get_permission_checker(required_permissions=["subscription"])),
    db: Session = Depends(get_db),
    create_template_service: CreateMessageTemplateService = Depends(
        Provide[Container.create_template_service]
    ),
) -> MessageTemplate:
    return create_template_service.exec(template_create, user, db=db)


@message_template_router.get("")
@inject
def get_all_templates(
    media: Optional[CampaignMedia] = None,
    user=Depends(get_permission_checker(required_permissions=[])),
    db: Session = Depends(get_db),
    get_template_service: GetMessageTemplateService = Depends(
        Provide[Container.get_template_service]
    ),
):
    return get_template_service.get_all_templates(media=media.value if media else None, db=db)


@message_template_router.get("/{template_id}")
@inject
def get_template_detail(
    template_id: str,
    user=Depends(get_permission_checker(required_permissions=[])),
    db: Session = Depends(get_db),
    get_template_service: GetMessageTemplateService = Depends(
        Provide[Container.get_template_service]
    ),
):
    return get_template_service.get_template_detail(template_id, db=db)


@message_template_router.put("/{template_id}")
@inject
def update_template(
    template_id: str,
    template_update: TemplateUpdate,
    user=Depends(get_permission_checker(required_permissions=["subscription"])),
    db: Session = Depends(get_db),
    update_template_service: UpdateMessageTemplateService = Depends(
        Provide[Container.update_template_service]
    ),
):
    update_template_service.exec(template_id, template_update, user, db=db)


@message_template_router.delete("/{template_id}", status_code=status.HTTP_204_NO_CONTENT)
@inject
def delete_template(
    template_id: str,
    user=Depends(get_permission_checker(required_permissions=["subscription"])),
    db: Session = Depends(get_db),
    delete_template_service: DeleteMessageTemplateService = Depends(
        Provide[Container.delete_template_service]
    ),
):
    delete_template_service.exec(template_id, db=db)


@message_template_router.get("/message/opt-out-number")
@inject
def get_opt_out_number(
    user=Depends(get_permission_checker(required_permissions=["subscription"])),
    db: Session = Depends(get_db),
    onboarding_service: BaseOnboardingService = Depends(Provide[Container.onboarding_service]),
) -> OptOutPhoneNumberResponse:
    return onboarding_service.get_opt_out_phone_number(user, db)
