from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, status

from src.auth.utils.permission_checker import get_permission_checker
from src.core.container import Container
from src.message_template.domain.message_template import MessageTemplate
from src.message_template.routes.dto.request.message_template_create import (
    TemplateCreate,
)
from src.message_template.service.create_message_template_service import (
    CreateMessageTemplateService,
)

message_template_router = APIRouter(
    tags=["Settings-message-template"],
)


@message_template_router.post("", status_code=status.HTTP_201_CREATED)
@inject
def create_message_template(
    template_create: TemplateCreate,
    user=Depends(get_permission_checker(required_permissions=[])),
    create_template_service: CreateMessageTemplateService = Depends(
        Provide[Container.create_template_service]
    ),
) -> MessageTemplate:
    return create_template_service.exec(template_create, user)


@message_template_router.get("")
@inject
def get_all_templates():
    pass


@message_template_router.get("/{template_id}")
@inject
def get_template_detail(template_id):
    pass


@message_template_router.put("/{template_id}")
def update_template():
    pass


@message_template_router.delete("/{template_id}")
@inject
def delete_template(template_id):
    pass
