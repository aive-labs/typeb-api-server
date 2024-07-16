from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from src.auth.utils.permission_checker import get_permission_checker
from src.campaign.routes.dto.request.campaign_create import CampaignCreate
from src.campaign.routes.dto.request.campaign_set_update import CampaignSetUpdate
from src.campaign.routes.dto.request.message_generate import MsgGenerationReq
from src.campaign.routes.dto.response.campaign_timeline_response import (
    CampaignTimelineResponse,
)
from src.campaign.routes.dto.response.exclusion_customer_detail import (
    ExcludeCustomerDetail,
)
from src.campaign.routes.port.create_campaign_usecase import CreateCampaignUseCase
from src.campaign.routes.port.generate_message_usecase import GenerateMessageUsecase
from src.campaign.routes.port.get_campaign_usecase import GetCampaignUseCase
from src.campaign.routes.port.update_campaign_set_usecase import (
    UpdateCampaignSetUseCase,
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
        campaign_id, campaign_set_update, user, db
    )
