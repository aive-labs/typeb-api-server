from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends

from src.auth.utils.permission_checker import get_permission_checker
from src.campaign.routes.port.reserve_campaigns_usecase import ReserveCampaignsUseCase
from src.core.container import Container
from src.core.database import get_db_session

campaign_dag_router = APIRouter(
    tags=["Campaign-Dag"],
)


@campaign_dag_router.post("/campaigns/{campaign_id}/send-reservation/{execution_date}")
@inject
async def reserve_campaigns(
    campaign_id: str,
    execution_date: str,
    reserve_campaign_service: ReserveCampaignsUseCase = Depends(
        dependency=Provide[Container.reserve_campaign_service]
    ),
    user=Depends(get_permission_checker(required_permissions=[])),
    db=Depends(get_db_session),
):
    return await reserve_campaign_service.reserve_campaigns(
        campaign_id, execution_date, user, db=db
    )
