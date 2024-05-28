from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, status

from src.audiences.routes.dto.response.audience_stat_info import AudienceStatsInfo
from src.audiences.routes.dto.response.audiences import AudienceResponse
from src.audiences.routes.port.usecase.delete_audience_usecase import (
    DeleteAudienceUsecase,
)
from src.audiences.routes.port.usecase.get_audience_usecase import GetAudienceUsecase
from src.auth.utils.permission_checker import get_permission_checker
from src.core.container import Container

audience_router = APIRouter(tags=["audience"])


@audience_router.get("/audiences", response_model=AudienceResponse)
@inject
def get_audiences(
    is_exclude: bool | None = None,
    get_audience_service: GetAudienceUsecase = Depends(
        Provide[Container.get_audience_service]
    ),
    user=Depends(
        get_permission_checker(
            required_permissions=["gnb_permissions:target_audience:read"]
        )
    ),
):

    # get_all_audience에서 리턴 타입이 dictionary 형태임
    return get_audience_service.get_all_audiences(user, is_exclude)


@audience_router.get("/audiences/{audience_id}/info", response_model=AudienceStatsInfo)
def get_audience_detail(
    audience_id: str,
    user=Depends(
        get_permission_checker(
            required_permissions=["gnb_permissions:target_audience:read"]
        )
    ),
    get_audience_service: GetAudienceUsecase = Depends(
        Provide[Container.get_audience_service]
    ),
):
    return get_audience_service.get_audience_details(audience_id)


@audience_router.delete(
    "/audiences/{audience_id}", status_code=status.HTTP_204_NO_CONTENT
)
def delete_audience(
    audience_id: str,
    user=Depends(
        get_permission_checker(
            required_permissions=["gnb_permissions:target_audience:delete"]
        )
    ),
    delete_audience_service: DeleteAudienceUsecase = Depends(
        Provide[Container.delete_audience_service]
    ),
):
    """타겟 오디언스 삭제: 타겟 오디언스 오브젝트를 삭제하는 API
    -삭제 불가 오브젝트
     1. 세그먼트 타겟 -> 에러 처리

    -삭제 가능 상태:
     1. 미활성 ("inactive")
     2. 기간 만료 ("expired") -> update

    -삭제 테이블:
    1. audiences
    2. audience_queries
    3. audience_count_by_month
    4. audience_stats
    5. primary_rep_product
    6. audience_upload

    -exclude objectid from cus_cd
    1. cust_campaign_objects
    """
    delete_audience_service.delete_audience(audience_id=audience_id)
