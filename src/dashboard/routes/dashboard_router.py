from datetime import datetime, timedelta
from typing import Optional

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from src.core.container import Container
from src.core.db_dependency import get_db
from src.dashboard.infra.dto.response.campaign_audience_stats_response import (
    CampaignAudienceStatsResponse,
)
from src.dashboard.infra.dto.response.campaign_stats_response import (
    CampaignStatsResponse,
)
from src.dashboard.infra.dto.response.campaign_summary_stats_response import (
    CampaignSummaryStatsResponse,
)
from src.dashboard.service.get_audience_stats_service import GetAudienceStatsService
from src.dashboard.service.get_campaign_group_stats_service import (
    GetCampaignGroupStatsService,
)
from src.dashboard.service.get_campaign_stats_service import GetCampaignStatsService
from src.search.routes.dto.id_with_item_response import IdWithItem

dashboard_router = APIRouter(
    tags=["Dashboard"],
)


@dashboard_router.get("/campaign-stats-v2")
@inject
async def get_campaign_stats_v2(
    start_date: str | None = (datetime.now() - timedelta(days=30)).strftime("%Y%m%d"),
    end_date: str | None = datetime.now().strftime("%Y%m%d"),
    db: Session = Depends(get_db),
    get_campaign_stats_service: GetCampaignStatsService = Depends(
        Provide[Container.get_campaign_stats_service]
    ),
):
    campaign_summary_stats_df, campaign_stats_df = (
        get_campaign_stats_service.get_campaign_stats_result(
            db=db, start_date=start_date, end_date=end_date
        )
    )
    return {
        "campaign_summary_stats": [
            CampaignSummaryStatsResponse.model_validate(stat)
            for stat in campaign_summary_stats_df.to_dict(orient="records")
        ],
        "campaign_stats": [
            CampaignStatsResponse.model_validate(stat)
            for stat in campaign_stats_df.to_dict(orient="records")
        ],
    }


@dashboard_router.get("/campaign-group-stats/options")
@inject
async def get_campaign_group_stats_options(
    db: Session = Depends(get_db),
    get_campaign_group_stats_service: GetCampaignGroupStatsService = Depends(
        Provide[Container.get_campaign_group_stats_service]
    ),
):
    codes = get_campaign_group_stats_service.get_campaign_group_stats_codes()
    return {
        "group_code_lv1": [IdWithItem(id=k, name=v) for k, v in codes.items()],
        "group_code_lv2": [IdWithItem(id=k, name=v) for k, v in codes.items()],
    }


@dashboard_router.get("/campaign-group-stats-v2")
@inject
async def get_campaign_group_stats_v2(
    start_date: str | None = (datetime.now() - timedelta(days=30)).strftime("%Y%m%d"),
    end_date: str | None = datetime.now().strftime("%Y%m%d"),
    group_code_lv1: Optional[str] = None,
    group_code_lv2: Optional[str] = None,
    db: Session = Depends(get_db),
    get_campaign_group_stats_service: GetCampaignGroupStatsService = Depends(
        Provide[Container.get_campaign_group_stats_service]
    ),
):
    if not group_code_lv1 and group_code_lv2:
        raise HTTPException(
            status_code=400, detail="그룹 구분2가 주어지면, 그룹 구분1도 주어져야 합니다."
        )

    campaign_group_stats_df, campaign_lst_df = (
        get_campaign_group_stats_service.get_campaign_group_stats_result(
            db=db,
            start_date=start_date,
            end_date=end_date,
            group_code_lv1=group_code_lv1,
            group_code_lv2=group_code_lv2,
        )
    )
    return {
        "group_stats": list(campaign_group_stats_df.to_dict(orient="records")),
        "campaign_options": [
            IdWithItem(id=opt["campaign_id"], name=opt["campaign_name"])
            for opt in campaign_lst_df.to_dict(orient="records")
        ],
        "group_code_lv1_options": [
            IdWithItem(id=opt, name=str(opt))
            for opt in campaign_group_stats_df["group_code_lv1"].unique()
        ],
        "group_code_lv2_options": [
            IdWithItem(id=opt, name=str(opt))
            for opt in campaign_group_stats_df["group_code_lv2"].unique()
        ],
    }


@dashboard_router.get("/audience-stats/options")
@inject
async def get_audience_stats_data(
    start_date: str | None = (datetime.now() - timedelta(days=30)).strftime("%Y%m%d"),
    end_date: str | None = datetime.now().strftime("%Y%m%d"),
    db: Session = Depends(get_db),
    get_audience_stats_service: GetAudienceStatsService = Depends(
        Provide[Container.get_audience_stats_service]
    ),
):
    return get_audience_stats_service.get_audience_stats_options(db, start_date, end_date)


@dashboard_router.get("/audience-stats")
@inject
async def get_audience_stats(
    start_date: str | None = (datetime.now() - timedelta(days=30)).strftime("%Y%m%d"),
    end_date: str | None = datetime.now().strftime("%Y%m%d"),
    audience_id: str | None = None,
    db: Session = Depends(get_db),
    get_audience_stats_service: GetAudienceStatsService = Depends(
        Provide[Container.get_audience_stats_service]
    ),
):
    audience_stats_df = get_audience_stats_service.get_audience_stats_result(
        db, start_date, end_date, audience_id
    )
    return [
        CampaignAudienceStatsResponse.model_validate(stat)
        for stat in audience_stats_df.to_dict(orient="records")
    ]


@dashboard_router.get("/audience-stats/item-purchase")
@inject
async def get_audience_stats_item_purchase(
    audience_id: str,
    start_date: str | None = (datetime.now() - timedelta(days=30)).strftime("%Y%m%d"),
    end_date: str | None = datetime.now().strftime("%Y%m%d"),
    db: Session = Depends(get_db),
    get_audience_stats_service: GetAudienceStatsService = Depends(
        Provide[Container.get_audience_stats_service]
    ),
):
    product_name_stats, category_name_stats, rep_nm_stats = (
        get_audience_stats_service.get_audience_prch_item_result(
            db, audience_id, start_date, end_date
        )
    )
    return {
        "product_name_stats": list(product_name_stats.to_dict(orient="records")),
        "rep_nm_stats": list(rep_nm_stats.to_dict(orient="records")),
        "category_name_stats": list(category_name_stats.to_dict(orient="records")),
    }
