from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, BackgroundTasks, Depends, status
from fastapi.responses import StreamingResponse

from src.audiences.routes.dto.request.audience_create import AudienceCreate
from src.audiences.routes.dto.response.audience_stat_info import AudienceStatsInfo
from src.audiences.routes.dto.response.audience_variable_combinations import (
    AudienceVariableCombinations,
)
from src.audiences.routes.dto.response.audiences import AudienceResponse
from src.audiences.routes.port.usecase.create_audience_usecase import (
    CreateAudienceUseCase,
)
from src.audiences.routes.port.usecase.delete_audience_usecase import (
    DeleteAudienceUsecase,
)
from src.audiences.routes.port.usecase.download_audience_usecase import (
    DownloadAudienceUseCase,
)
from src.audiences.routes.port.usecase.get_audience_usecase import GetAudienceUseCase
from src.audiences.service.background.execute_target_audience_summary import (
    execute_target_audience_summary,
)
from src.auth.utils.permission_checker import get_permission_checker
from src.core.container import Container

audience_router = APIRouter(tags=["audience"])


@audience_router.get("/audiences", response_model=AudienceResponse)
@inject
def get_audiences(
    is_exclude: bool | None = None,
    get_audience_service: GetAudienceUseCase = Depends(
        Provide[Container.get_audience_service]
    ),
    user=Depends(get_permission_checker(required_permissions=[])),
):
    # get_all_audience에서 리턴 타입이 dictionary 형태임
    return get_audience_service.get_all_audiences(user, is_exclude)


@audience_router.get("/audiences/{audience_id}/info", response_model=AudienceStatsInfo)
@inject
def get_audience_detail(
    audience_id: str,
    user=Depends(get_permission_checker(required_permissions=[])),
    get_audience_service: GetAudienceUseCase = Depends(
        Provide[Container.get_audience_service]
    ),
):
    return get_audience_service.get_audience_details(audience_id)


@audience_router.post("/audiences", status_code=status.HTTP_201_CREATED)
@inject
def create_audience(
    audience_create: AudienceCreate,
    background_task: BackgroundTasks,
    create_audience_service: CreateAudienceUseCase = Depends(
        Provide[Container.create_audience_service]
    ),
    user=Depends(get_permission_checker([])),
):
    audience_id = create_audience_service.create_audience(
        audience_create=audience_create, user=user
    )

    background_task.add_task(execute_target_audience_summary, audience_id)


@audience_router.get(
    "/variable_combinations", response_model=AudienceVariableCombinations
)
@inject
def get_audience_variable_combinations(
    user=Depends(get_permission_checker([])),
    create_audience_service: CreateAudienceUseCase = Depends(
        Provide[Container.create_audience_service]
    ),
):
    """생성 변수 조합 정보 조회:  타겟 오디언스 생성 변수에 대한 옵션 정보를 내려주는 API"""
    predefined_variables = create_audience_service.get_audience_variable_combinations(
        user
    )
    options_by_cell = create_audience_service.get_option_items()

    return AudienceVariableCombinations(
        predefined_variables=predefined_variables, options_by_data_type=options_by_cell
    )


@audience_router.delete(
    "/audiences/{audience_id}", status_code=status.HTTP_204_NO_CONTENT
)
@inject
def delete_audience(
    audience_id: str,
    user=Depends(get_permission_checker(required_permissions=[])),
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


@audience_router.get("/audiences/{audience_id}/download")
@inject
def download_audience(
    audience_id: str,
    user=Depends(get_permission_checker(required_permissions=[])),
    download_audience_service: DownloadAudienceUseCase = Depends(
        Provide[Container.download_audience_service]
    ),
):
    """타겟 오디언스 다운로드: 타겟 오디언스 다운로드 API"""

    data = download_audience_service.exec(audience_id)

    return StreamingResponse(
        iter([data.to_csv(index=False)]),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={audience_id}.csv"},
    )
