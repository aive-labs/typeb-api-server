from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from src.auth.utils.permission_checker import get_permission_checker
from src.campaign.routes.dto.request.campaign_create import CampaignCreate
from src.campaign.routes.dto.request.campaign_progress_request import (
    CampaignProgressRequest,
)
from src.campaign.routes.dto.request.campaign_set_group_message_request import (
    CampaignSetGroupMessageRequest,
)
from src.campaign.routes.dto.request.campaign_set_group_update import (
    CampaignSetGroupUpdate,
)
from src.campaign.routes.dto.request.campaign_set_message_confirm_request import (
    CampaignSetMessageConfirmReqeust,
)
from src.campaign.routes.dto.request.campaign_set_message_use_request import (
    CampaignSetMessageUseRequest,
)
from src.campaign.routes.dto.request.campaign_set_update import CampaignSetUpdate
from src.campaign.routes.dto.request.message_generate import MsgGenerationReq
from src.campaign.routes.dto.response.campaign_set_description_response import (
    CampaignSetDescriptionResponse,
)
from src.campaign.routes.dto.response.campaign_set_group_update_response import (
    CampaignSetGroupUpdateResponse,
)
from src.campaign.routes.dto.response.campaign_timeline_response import (
    CampaignTimelineResponse,
)
from src.campaign.routes.dto.response.exclusion_customer_detail import (
    ExcludeCustomerDetail,
)
from src.campaign.routes.dto.response.update_campaign_set_group_message_response import (
    UpdateCampaignSetGroupMessageResponse,
)
from src.campaign.routes.port.confirm_campaign_set_group_message_usecase import (
    ConfirmCampaignSetGroupMessageUseCase,
)
from src.campaign.routes.port.create_campaign_usecase import CreateCampaignUseCase
from src.campaign.routes.port.generate_message_usecase import GenerateMessageUsecase
from src.campaign.routes.port.get_campaign_set_description_usecase import (
    GetCampaignSetDescriptionUseCase,
)
from src.campaign.routes.port.get_campaign_usecase import GetCampaignUseCase
from src.campaign.routes.port.update_campaign_progress_usecase import (
    UpdateCampaignProgressUseCase,
)
from src.campaign.routes.port.update_campaign_set_message_group_usecase import (
    UpdateCampaignSetMessageGroupUseCase,
)
from src.campaign.routes.port.update_campaign_set_usecase import (
    UpdateCampaignSetUseCase,
)
from src.campaign.routes.port.update_message_use_status_usecase import (
    UpdateMessageUseStatusUseCase,
)
from src.core.container import Container
from src.core.database import get_db_session

campaign_router = APIRouter(tags=["Campaign-management"])


@campaign_router.get("/campaigns")
@inject
def get_campaigns(
    start_date: str,
    end_date: str,
    user=Depends(get_permission_checker(required_permissions=[])),
    get_campaign_service: GetCampaignUseCase = Depends(
        dependency=Provide[Container.get_campaign_service]
    ),
):
    return get_campaign_service.get_campaigns(start_date, end_date, user)


@campaign_router.get("/timeline/{campaign_id}")
@inject
def get_campaign_timeline(
    campaign_id: str,
    user=Depends(get_permission_checker(required_permissions=[])),
    db: Session = Depends(get_db_session),
    get_campaign_service: GetCampaignUseCase = Depends(
        dependency=Provide[Container.get_campaign_service]
    ),
) -> list[CampaignTimelineResponse]:
    return get_campaign_service.get_timeline(campaign_id, db=db)


@campaign_router.post("/campaigns")
@inject
def create_campaign(
    campaign_create: CampaignCreate,
    user=Depends(get_permission_checker(required_permissions=[])),
    db=Depends(get_db_session),
    create_campaign_service: CreateCampaignUseCase = Depends(
        dependency=Provide[Container.create_campaign_service]
    ),
):
    return create_campaign_service.create_campaign(campaign_create, user, db=db)


@campaign_router.get("/campaigns/{campaign_id}")
@inject
def get_campaign_detail(
    campaign_id: str,
    user=Depends(get_permission_checker(required_permissions=[])),
    db=Depends(get_db_session),
    get_campaign_service: GetCampaignUseCase = Depends(
        dependency=Provide[Container.get_campaign_service]
    ),
):
    return get_campaign_service.get_campaign_detail(campaign_id, user, db=db)


@campaign_router.post("/campaigns/generate-message")
@inject
def generate_message(
    message_generate: MsgGenerationReq,
    user=Depends(get_permission_checker(required_permissions=[])),
    generate_message_service: GenerateMessageUsecase = Depends(
        dependency=Provide[Container.generate_message_service]
    ),
):
    return generate_message_service.generate_message(message_generate, user)


@campaign_router.get("/campaigns/excluded-custs/{campaign_id}")
@inject
def get_excluded_customer(
    campaign_id: str,
    user=Depends(get_permission_checker(required_permissions=[])),
    db=Depends(get_db_session),
    get_campaign_service: GetCampaignUseCase = Depends(
        dependency=Provide[Container.get_campaign_service]
    ),
) -> ExcludeCustomerDetail:
    return get_campaign_service.get_exclude_customer(campaign_id, user, db=db)


@campaign_router.put("/campaigns/{campaign_id}/set")
@inject
def create_or_update_campaign_set(
    campaign_id: str,
    campaign_set_update: CampaignSetUpdate,
    user=Depends(get_permission_checker(required_permissions=[])),
    db=Depends(get_db_session),
    update_campaign_set_service: UpdateCampaignSetUseCase = Depends(
        dependency=Provide[Container.update_campaign_set_service]
    ),
):
    return update_campaign_set_service.update_campaign_set(
        campaign_id, campaign_set_update, user, db=db
    )


@campaign_router.put("/campaigns/{campaign_id}/{set_seq}/group")
@inject
def update_campaign_set_message_group(
    campaign_id: str,
    set_seq: int,
    set_group_updated: CampaignSetGroupUpdate,
    user=Depends(get_permission_checker(required_permissions=[])),
    db=Depends(get_db_session),
    update_campaign_set_message_group_service: UpdateCampaignSetMessageGroupUseCase = Depends(
        dependency=Provide[Container.update_campaign_set_message_group_service]
    ),
) -> CampaignSetGroupUpdateResponse:
    return update_campaign_set_message_group_service.update_campaign_set_message_group(
        campaign_id, set_seq, set_group_updated, user, db=db
    )


@campaign_router.patch("/campaigns/{campaign_id}")
@inject
def patch_campaign_progress(
    campaign_id: str,
    progress_req: CampaignProgressRequest,
    user=Depends(get_permission_checker(required_permissions=[])),
    db=Depends(get_db_session),
    update_campaign_progress_service: UpdateCampaignProgressUseCase = Depends(
        dependency=Provide[Container.update_campaign_progress_service]
    ),
):
    update_campaign_progress_service.exec(campaign_id, progress_req.progress, db=db)

    return {"res": True}


@campaign_router.put("/campaigns/{campaign_id}/message/{set_group_msg_seq}")
@inject
def update_campaign_message(
    campaign_id: str,
    set_group_msg_seq: int,
    msg_input: CampaignSetGroupMessageRequest,
    user=Depends(get_permission_checker(required_permissions=[])),
    db=Depends(get_db_session),
    update_campaign_set_message_group_service: UpdateCampaignSetMessageGroupUseCase = Depends(
        dependency=Provide[Container.update_campaign_set_message_group_service]
    ),
) -> UpdateCampaignSetGroupMessageResponse:
    return update_campaign_set_message_group_service.update_campaign_set_messages_contents(
        campaign_id, set_group_msg_seq, msg_input, user, db=db
    )


@campaign_router.put("/campaigns/{campaign_id}/message/{set_seq}/is_confirmed")
@inject
def update_set_message_confirmed(
    campaign_id: str,
    set_seq: int,
    is_confirmed_obj: CampaignSetMessageConfirmReqeust,
    user=Depends(get_permission_checker(required_permissions=[])),
    db=Depends(get_db_session),
    confirm_campaign_set_group_message: ConfirmCampaignSetGroupMessageUseCase = Depends(
        dependency=Provide[Container.confirm_campaign_set_group_message]
    ),
):
    confirm_campaign_set_group_message.exec(campaign_id, set_seq, is_confirmed_obj, user, db=db)
    return {"status": "success"}


@campaign_router.put("/campaigns/{campaign_id}/message/{set_group_msg_seq}/is_used")
@inject
def update_campaign_message_use_status(
    campaign_id: str,
    set_group_msg_seq: int,
    is_used_obj: CampaignSetMessageUseRequest,
    user=Depends(get_permission_checker(required_permissions=[])),
    db=Depends(get_db_session),
    update_message_use_status_service: UpdateMessageUseStatusUseCase = Depends(
        dependency=Provide[Container.update_message_use_status_service]
    ),
):
    update_message_use_status_service.exec(campaign_id, set_group_msg_seq, is_used_obj, user, db=db)

    return {"res": True}


@campaign_router.get("/campaign/{campaign_id}/set-description")
def get_campaign_set_description(
    campaign_id: str,
    user=Depends(get_permission_checker(required_permissions=[])),
    db=Depends(get_db_session),
    get_campaign_set_description: GetCampaignSetDescriptionUseCase = Depends(
        dependency=Provide[Container.get_campaign_set_description]
    ),
) -> CampaignSetDescriptionResponse:
    get_campaign_set_description.exec(campaign_id)
