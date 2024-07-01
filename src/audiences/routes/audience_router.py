import pathlib
from io import BytesIO

import pandas as pd
from dependency_injector.wiring import Provide, inject
from fastapi import (
    APIRouter,
    BackgroundTasks,
    Depends,
    HTTPException,
    UploadFile,
    status,
)
from fastapi.responses import FileResponse, StreamingResponse

from src.audiences.enums.audience_create_type import AudienceCreateType
from src.audiences.enums.csv_template import CsvTemplates
from src.audiences.enums.target_audience_update_cycle import TargetAudienceUpdateCycle
from src.audiences.routes.dto.request.audience_create import AudienceCreate
from src.audiences.routes.dto.request.audience_update import AudienceUpdate
from src.audiences.routes.dto.response.audience_stat_info import AudienceStatsInfo
from src.audiences.routes.dto.response.audience_variable_combinations import (
    AudienceVariableCombinations,
)
from src.audiences.routes.dto.response.audiences import AudienceResponse
from src.audiences.routes.dto.response.target_strategy_combination import (
    TargetStrategyCombination,
)
from src.audiences.routes.dto.response.upload_condition_response import (
    AudienceCreationOptionsResponse,
)
from src.audiences.routes.port.usecase.create_audience_usecase import (
    CreateAudienceUseCase,
)
from src.audiences.routes.port.usecase.csv_upload_usecase import CSVUploadUseCase
from src.audiences.routes.port.usecase.delete_audience_usecase import (
    DeleteAudienceUseCase,
)
from src.audiences.routes.port.usecase.download_audience_usecase import (
    DownloadAudienceUseCase,
)
from src.audiences.routes.port.usecase.get_audience_creation_options_usecase import (
    GetAudienceCreationOptionsUseCase,
)
from src.audiences.routes.port.usecase.get_audience_usecase import GetAudienceUseCase
from src.audiences.routes.port.usecase.update_cycle_usecase import (
    AudienceUpdateCycleUseCase,
)
from src.audiences.service.background.execute_target_audience_summary import (
    execute_target_audience_summary,
)
from src.auth.utils.permission_checker import get_permission_checker
from src.core.container import Container

audience_router = APIRouter(tags=["Audience-management"])


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


@audience_router.get(
    "/audiences/{audience_id}/summary", response_model=AudienceStatsInfo
)
@inject
def get_audience_detail(
    audience_id: str,
    user=Depends(get_permission_checker(required_permissions=[])),
    get_audience_service: GetAudienceUseCase = Depends(
        Provide[Container.get_audience_service]
    ),
):
    return get_audience_service.get_audience_stat_details(audience_id)


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


@audience_router.get("/target-strategy-combinations")
@inject
def get_audience_target_strategy_combinations(
    user=Depends(get_permission_checker([])),
    create_audience_service: CreateAudienceUseCase = Depends(
        Provide[Container.create_audience_service]
    ),
) -> TargetStrategyCombination:
    """타겟 전략에 대한 필터 조건을 조회하는 API"""
    return create_audience_service.get_audience_target_strategy_combinations()


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
    """생성 변수 조합 정보 조회:  타겟 오디언스가 어떤 생성 조건으로 만들어졌는지에 대한 옵션 정보를 내려주는 API"""
    predefined_variables = create_audience_service.get_audience_variable_combinations(
        user
    )
    options_by_cell = create_audience_service.get_option_items()

    return AudienceVariableCombinations(
        predefined_variables=predefined_variables, options_by_data_type=options_by_cell
    )


@audience_router.get("/audiences/{audience_id}")
@inject
def get_audience_creation_options(
    audience_id: str,
    user=Depends(get_permission_checker([])),
    get_audience_service: GetAudienceUseCase = Depends(
        Provide[Container.get_audience_service]
    ),
    get_audience_creation_option: GetAudienceCreationOptionsUseCase = Depends(
        Provide[Container.get_audience_creation_option]
    ),
) -> AudienceCreationOptionsResponse:
    """타겟 오디언스 생성조건 조회:  타겟 오디언스 생성 조건을 조회하는 API"""
    audience = get_audience_service.get_audience_details(audience_id)

    if audience.create_type_code == AudienceCreateType.Filter.value:
        return get_audience_creation_option.get_filter_conditions(audience_id)
    else:
        return get_audience_creation_option.get_csv_uploaded_data(audience_id)


@audience_router.put("/audiences/{audience_id}/creation-options")
@inject
def update_audience_creation_options(
    audience_id: str,
    audience_update: AudienceUpdate,
    user=Depends(get_permission_checker([])),
    # background_task: BackgroundTasks,
):
    """타겟 오디언스 생성조건 수정:  타겟 오디언스 생성 조건을 조회하는 API

    -수정 가능 상태:
     1. 미활성 ("inactive")

    * create_type이 변경되는 경우 -> 삭제 & 재생성

    삭제 테이블 (create_type이 변경되는 경우)
    1. audience_filter_conditions | audience_upload_conditions


    * create_type이 변경되지 않는 경우 -> 재생성

    -수정 테이블:
    1. audiences
    2. audience_filter_conditions | audience_upload_conditions
    3. audience_count_by_month
    4. audience_stats
    5. primary_rep_product

    -update objectid for cus_cd
    1. cust_campaign_objects
    """

    return {"result": True}


@audience_router.delete(
    "/audiences/{audience_id}", status_code=status.HTTP_204_NO_CONTENT
)
@inject
def delete_audience(
    audience_id: str,
    user=Depends(get_permission_checker(required_permissions=[])),
    delete_audience_service: DeleteAudienceUseCase = Depends(
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
    delete_audience_service.exec(audience_id=audience_id)


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


@audience_router.get("/audiences/upload/template")
def get_csv_template(user=Depends(get_permission_checker(required_permissions=[]))):
    """타겟 오디언스 csv 템플릿 조회:  csv 템플릿 파일을 내려주는 API"""
    template_dir = pathlib.Path.cwd() / "src/audiences/resources/message_template"
    filename = f"{template_dir}/upload_templates.zip"

    return FileResponse(
        filename,
        headers={"Content-Disposition": "attachment; filename=upload_templates"},
    )


@audience_router.post("/audiences/upload/check")
@inject
async def check_csv_template(
    csv_file: UploadFile,
    user=Depends(get_permission_checker(required_permissions=[])),
    csv_upload_service: CSVUploadUseCase = Depends(
        Provide[Container.csv_upload_service]
    ),
):
    """타겟 오디언스 csv 파일 업로드 체크:  오디언스 생성 대상 csv 업로드 후 결과를 체크하는 API"""

    # 업로드 csv파일을 dataframe으로 로드
    contents = await csv_file.read()
    file_as_bytes = BytesIO(contents)
    df = pd.read_csv(file_as_bytes, dtype=str)

    template_type = list(df.columns)[0]  # cus_cd or shop_cd
    uploaded_rows = list(df[template_type].astype(str))

    # #업로드 템플릿 식별 후 결과 메세지 출력
    templates_members = CsvTemplates.get_eums()
    for template in templates_members:
        if template["_name_"] == template_type.lower():
            res_sentence, checked_list = csv_upload_service.check_audience_csv_file(
                uploaded_rows=uploaded_rows, template_enum=template
            )
            return {
                "result": res_sentence,
                "type": template["_name_"],
                "upload_count": len(uploaded_rows),
                "checked_list": checked_list,
            }

    raise Exception("파일이 템플릿과 일치하지 않습니다.")


@audience_router.patch(
    "/audiences/{audience_id}/update-cycle", status_code=status.HTTP_204_NO_CONTENT
)
@inject
def audience_update_cycles(
    audience_id: str,
    cycle: TargetAudienceUpdateCycle,
    user=Depends(get_permission_checker(required_permissions=[])),
    audience_update_cycle_service: AudienceUpdateCycleUseCase = Depends(
        Provide[Container.audience_update_cycle_service]
    ),
):
    """타겟 오디언스 업데이트 주기: 타겟 오디언스의 업데이트 주기를 변경하는 API"""
    if user.role_id not in ["admin", "operator"]:
        raise HTTPException(
            status_code=403,
            detail={"code": "modify/03", "message": "수정 권한이 없는 사용자입니다."},
        )

    audience_update_cycle_service.exec(audience_id, cycle.value)
