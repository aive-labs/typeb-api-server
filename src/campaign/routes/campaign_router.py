from typing import Optional

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, File, UploadFile, status
from sqlalchemy.orm import Session
from starlette.background import BackgroundTasks

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
from src.campaign.routes.dto.request.message_generate import (
    CarouselMsgGenerationReq,
    MsgGenerationReq,
)
from src.campaign.routes.dto.request.test_send_request import TestSendRequest
from src.campaign.routes.dto.response.campaign_set_description_response import (
    CampaignSetDescriptionResponse,
)
from src.campaign.routes.dto.response.campaign_set_group_update_response import (
    CampaignSetGroupUpdateResponse,
)
from src.campaign.routes.dto.response.campaign_summary_response import (
    CampaignSummaryResponse,
)
from src.campaign.routes.dto.response.campaign_timeline_response import (
    CampaignTimelineResponse,
)
from src.campaign.routes.dto.response.exclusion_customer_detail import (
    ExcludeCustomerDetail,
)
from src.campaign.routes.dto.response.generate_message_response import GeneratedMessage
from src.campaign.routes.dto.response.set_group_seq_with_message_response import (
    SetGroupSeqWithMessageResponse,
)
from src.campaign.routes.dto.response.update_campaign_set_group_message_response import (
    UpdateCampaignSetGroupMessageResponse,
)
from src.campaign.routes.port.approve_campaign_usecase import ApproveCampaignUseCase
from src.campaign.routes.port.confirm_campaign_set_group_message_usecase import (
    ConfirmCampaignSetGroupMessageUseCase,
)
from src.campaign.routes.port.create_campaign_summary_usecase import (
    CreateCampaignSummaryUseCase,
)
from src.campaign.routes.port.create_campaign_usecase import CreateCampaignUseCase
from src.campaign.routes.port.delete_campaign_usecase import DeleteCampaignUseCase
from src.campaign.routes.port.delete_image_for_message_usecase import (
    DeleteImageForMessageUseCase,
)
from src.campaign.routes.port.generate_message_usecase import GenerateMessageUsecase
from src.campaign.routes.port.get_campaign_set_description_usecase import (
    GetCampaignSetDescriptionUseCase,
)
from src.campaign.routes.port.get_campaign_usecase import GetCampaignUseCase
from src.campaign.routes.port.test_message_send_usecase import TestSendMessageUseCase
from src.campaign.routes.port.update_campaign_progress_usecase import (
    UpdateCampaignProgressUseCase,
)
from src.campaign.routes.port.update_campaign_set_confirm_usecase import (
    UpdateCampaignSetStatusToConfirmUseCase,
)
from src.campaign.routes.port.update_campaign_set_message_group_usecase import (
    UpdateCampaignSetMessageGroupUseCase,
)
from src.campaign.routes.port.update_campaign_set_usecase import (
    UpdateCampaignSetUseCase,
)
from src.campaign.routes.port.update_campaign_usecase import UpdateCampaignUseCase
from src.campaign.routes.port.update_message_use_status_usecase import (
    UpdateMessageUseStatusUseCase,
)
from src.campaign.routes.port.upload_image_for_message_usecase import (
    UploadImageForMessageUseCase,
)
from src.main.container import Container
from src.main.db_dependency import get_db
from src.search.routes.port.base_search_service import BaseSearchService

campaign_router = APIRouter(tags=["Campaign-management"])


@campaign_router.get("/campaigns")
@inject
def get_campaigns(
    start_date: str,
    end_date: str,
    user=Depends(get_permission_checker(required_permissions=[])),
    db: Session = Depends(get_db),
    get_campaign_service: GetCampaignUseCase = Depends(
        dependency=Provide[Container.get_campaign_service]
    ),
):
    return get_campaign_service.get_campaigns(start_date, end_date, user, db=db)


@campaign_router.get("/timeline/{campaign_id}")
@inject
def get_campaign_timeline(
    campaign_id: str,
    user=Depends(get_permission_checker(required_permissions=[])),
    db: Session = Depends(get_db),
    get_campaign_service: GetCampaignUseCase = Depends(
        dependency=Provide[Container.get_campaign_service]
    ),
) -> list[CampaignTimelineResponse]:
    return get_campaign_service.get_timeline(campaign_id, db=db)


@campaign_router.put("/campaigns/{campaign_id}")
@inject
def update_campaign(
    campaign_id: str,
    campaign_update: CampaignCreate,
    user=Depends(get_permission_checker(required_permissions=["subscription"])),
    db=Depends(get_db),
    update_campaign_service: UpdateCampaignUseCase = Depends(
        Provide[Container.update_campaign_service]
    ),
):
    return update_campaign_service.exec(campaign_id, campaign_update, user, db=db)


@campaign_router.post("/campaigns")
@inject
def create_campaign(
    campaign_create: CampaignCreate,
    user=Depends(get_permission_checker(required_permissions=["subscription"])),
    db=Depends(get_db),
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
    db=Depends(get_db),
    get_campaign_service: GetCampaignUseCase = Depends(
        dependency=Provide[Container.get_campaign_service]
    ),
):
    return get_campaign_service.get_campaign_detail(campaign_id, user, db=db)


@campaign_router.post("/campaigns/generate-message")
@inject
def generate_message(
    message_generate: MsgGenerationReq,
    user=Depends(get_permission_checker(required_permissions=["subscription"])),
    db=Depends(get_db),
    generate_message_service: GenerateMessageUsecase = Depends(
        dependency=Provide[Container.generate_message_service]
    ),
) -> list[GeneratedMessage]:
    return generate_message_service.generate_message(message_generate, user, db=db)


@campaign_router.post("/campaigns/generate-carousel-message")
@inject
def generate_carousel_message_request(
    carousel_message_generate: CarouselMsgGenerationReq,
    user=Depends(get_permission_checker(required_permissions=["subscription"])),
    db=Depends(get_db),
    generate_message_service: GenerateMessageUsecase = Depends(
        dependency=Provide[Container.generate_message_service]
    ),
):
    return generate_message_service.generate_carousel_message(
        carousel_message_generate, user, db=db
    )


@campaign_router.get("/campaigns/excluded-custs/{campaign_id}")
@inject
def get_excluded_customer(
    campaign_id: str,
    user=Depends(get_permission_checker(required_permissions=[])),
    db=Depends(get_db),
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
    user=Depends(get_permission_checker(required_permissions=["subscription"])),
    db=Depends(get_db),
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
    user=Depends(get_permission_checker(required_permissions=["subscription"])),
    db=Depends(get_db),
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
    user=Depends(get_permission_checker(required_permissions=["subscription"])),
    db=Depends(get_db),
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
    user=Depends(get_permission_checker(required_permissions=["subscription"])),
    db=Depends(get_db),
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
    user=Depends(get_permission_checker(required_permissions=["subscription"])),
    db=Depends(get_db),
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
    user=Depends(get_permission_checker(required_permissions=["subscription"])),
    db=Depends(get_db),
    update_message_use_status_service: UpdateMessageUseStatusUseCase = Depends(
        dependency=Provide[Container.update_message_use_status_service]
    ),
):
    update_message_use_status_service.exec(campaign_id, set_group_msg_seq, is_used_obj, user, db=db)

    return {"res": True}


@campaign_router.get("/campaign/{campaign_id}/set-description")
@inject
def get_campaign_set_description(
    campaign_id: str,
    user=Depends(get_permission_checker(required_permissions=[])),
    db=Depends(get_db),
    get_campaign_set_description_service: GetCampaignSetDescriptionUseCase = Depends(
        dependency=Provide[Container.get_campaign_set_description_service]
    ),
) -> CampaignSetDescriptionResponse:
    return get_campaign_set_description_service.exec(campaign_id, db)


@campaign_router.patch("/campaign/{campaign_id}/set-confirm/{set_seq}")
@inject
def update_campaign_set_confirmed(
    campaign_id: str,
    set_seq: int,
    user=Depends(get_permission_checker(required_permissions=["subscription"])),
    db=Depends(get_db),
    update_campaign_set_confirm_service: UpdateCampaignSetStatusToConfirmUseCase = Depends(
        dependency=Provide[Container.update_campaign_set_confirm_service]
    ),
):
    update_campaign_set_confirm_service.campaign_set_status_to_confirm(campaign_id, set_seq, db=db)
    return {"res": "success"}


@campaign_router.patch("/campaign/{campaign_id}/set-confirm")
@inject
def update_campaign_set_all_confirm(
    campaign_id: str,
    user=Depends(get_permission_checker(required_permissions=[])),
    db=Depends(get_db),
    update_campaign_set_confirm_service: UpdateCampaignSetStatusToConfirmUseCase = Depends(
        dependency=Provide[Container.update_campaign_set_confirm_service]
    ),
):
    update_campaign_set_confirm_service.all_campaign_set_status_to_confirm(campaign_id, db=db)
    return {"res": "success"}


@campaign_router.get("/campaign/{campaign_id}/summary")
@inject
def get_campaign_summary(
    campaign_id: str,
    user=Depends(get_permission_checker(required_permissions=[])),
    db=Depends(get_db),
    campaign_summary_service: CreateCampaignSummaryUseCase = Depends(
        dependency=Provide[Container.campaign_summary_service]
    ),
) -> CampaignSummaryResponse:
    return campaign_summary_service.create_campaign_summary(campaign_id, db=db)


@campaign_router.post("/campaigns/{campaign_id}/status_change")
@inject
async def campaign_status_change(
    campaign_id: str,
    to_status: str,
    background_task: BackgroundTasks,
    reviewers: Optional[str] = None,
    user=Depends(get_permission_checker(required_permissions=["subscription"])),
    db=Depends(get_db),
    approve_campaign_service: ApproveCampaignUseCase = Depends(
        dependency=Provide[Container.approve_campaign_service]
    ),
):
    return await approve_campaign_service.exec(
        campaign_id, to_status, user, db=db, reviewers=reviewers
    )


@campaign_router.post("/campaigns/{campaign_id}/message/test-send")
@inject
async def test_message_send(
    campaign_id: str,
    test_send_request: TestSendRequest,
    user=Depends(get_permission_checker(required_permissions=["subscription"])),
    db=Depends(get_db),
    test_send_service: TestSendMessageUseCase = Depends(
        dependency=Provide[Container.test_send_service]
    ),
):
    await test_send_service.exec(campaign_id, test_send_request, user, db=db)


@campaign_router.delete("/campaigns/{campaign_id}", status_code=status.HTTP_204_NO_CONTENT)
@inject
def delete_campaign(
    campaign_id: str,
    user=Depends(get_permission_checker(required_permissions=["subscription"])),
    db=Depends(get_db),
    delete_campaign_service: DeleteCampaignUseCase = Depends(
        dependency=Provide[Container.delete_campaign_service]
    ),
):
    delete_campaign_service.exec(campaign_id, user, db=db)


@campaign_router.get("/campaigns/search/rep_items")
@inject
def get_campaign_set_rep_items(
    campaign_id: str,
    strategy_theme_id: str,
    audience_id: str,
    coupon_no: Optional[str],
    db: Session = Depends(get_db),
    user=Depends(get_permission_checker(required_permissions=[])),
    search_service: BaseSearchService = Depends(dependency=Provide[Container.search_service]),
):
    rep_nm_list = search_service.search_campaign_set_items(
        strategy_theme_id, audience_id, coupon_no, db=db
    )
    return {"rep_nm_list": rep_nm_list}


@campaign_router.post("/campaigns/{campaign_id}/resource/{set_group_msg_seq}")
@inject
async def upload_message_resources(
    campaign_id: str,
    set_group_msg_seq: int,
    files: list[UploadFile] = File(...),
    db: Session = Depends(get_db),
    user=Depends(get_permission_checker(required_permissions=["subscription"])),
    upload_image_for_message: UploadImageForMessageUseCase = Depends(
        dependency=Provide[Container.upload_image_for_message]
    ),
) -> dict:
    """이미지 업로드 API"""
    return await upload_image_for_message.exec(campaign_id, set_group_msg_seq, files, user, db=db)


@campaign_router.delete("/campaigns/{campaign_id}/resource/{set_group_msg_seq}")
@inject
async def delete_message_resources(
    campaign_id: str,
    set_group_msg_seq: int,
    db: Session = Depends(get_db),
    user=Depends(get_permission_checker(required_permissions=["subscription"])),
    delete_image_for_message: DeleteImageForMessageUseCase = Depends(
        dependency=Provide[Container.delete_image_for_message]
    ),
) -> SetGroupSeqWithMessageResponse:
    """이미지 업로드 API"""
    return await delete_image_for_message.exec(campaign_id, set_group_msg_seq, user, db=db)


@campaign_router.post("/campaigns/{campaign_id}/test-carousel")
@inject
def carousel_test(
    campaign_id: str,
    user=Depends(get_permission_checker(required_permissions=["subscription"])),
    db=Depends(get_db),
    approve_campaign_service: ApproveCampaignUseCase = Depends(
        dependency=Provide[Container.approve_campaign_service]
    ),
):
    result = approve_campaign_service.save_campaign_reservation(db, user, campaign_id, None)
    db.commit()
    return result
