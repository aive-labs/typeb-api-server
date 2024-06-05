from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends

from src.auth.utils.permission_checker import get_permission_checker
from src.campaign.routes.dto.request.campaign_create import CampaignCreate
from src.campaign.routes.port.create_campaign_usecase import CreateCampaignUsecase
from src.campaign.routes.port.get_campaign_usecase import GetCampaignUsecase
from src.core.container import Container

campaign_router = APIRouter(tags=["Campaign-managemnet"])


@campaign_router.get("/campaigns")
@inject
def get_campaigns(
    start_date: str,
    end_date: str,
    user=Depends(
        get_permission_checker(required_permissions=["gnb_permissions:campaign:read"])
    ),
    get_campaign_service: GetCampaignUsecase = Depends(
        dependency=Provide[Container.get_campaign_service]
    ),
):
    return get_campaign_service.get_campaigns(start_date, end_date, user)


@campaign_router.post("/campaigns")
@inject
def create_campaign(
    campaign_create: CampaignCreate,
    user=Depends(
        get_permission_checker(required_permissions=["gnb_permissions:campaign:create"])
    ),
    create_campaign_service: CreateCampaignUsecase = Depends(
        dependency=Provide[Container.create_campaign_service]
    ),
):
    return create_campaign_service.create_campaign(campaign_create, user)
