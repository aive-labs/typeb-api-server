from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from src.auth.utils.permission_checker import get_permission_checker
from src.campaign.routes.dto.request.campaign_create import CampaignCreate
from src.campaign.routes.dto.response.campaign_timeline_response import (
    CampaignTimelineResponse,
)
from src.campaign.routes.port.create_campaign_usecase import CreateCampaignUsecase
from src.campaign.routes.port.get_campaign_usecase import GetCampaignUseCase
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
    create_campaign_service: CreateCampaignUsecase = Depends(
        dependency=Provide[Container.create_campaign_service]
    ),
):
    return create_campaign_service.create_campaign(campaign_create, user)
