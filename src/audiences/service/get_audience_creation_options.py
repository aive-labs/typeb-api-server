from src.audiences.enums.csv_template import CsvTemplates
from src.audiences.routes.dto.response.upload_condition_response import (
    AudienceCreationOptionsResponse,
    UploadOptionResponse,
)
from src.audiences.routes.port.usecase.get_audience_creation_options_usecase import (
    GetAudienceCreationOptionsUseCase,
)
from src.audiences.service.port.base_audience_repository import BaseAudienceRepository


class GetAudienceCreationOptions(GetAudienceCreationOptionsUseCase):

    def __init__(self, audience_repository: BaseAudienceRepository):
        self.audience_repository = audience_repository

    def get_filter_conditions(self, audience_id: str):
        """타겟 오디언스 생성 정보를 내려주는 함수"""

        # res = {}
        # conditions_listofdic = [
        #     row._asdict() for row in get_db_filter_conditions(db, audience_id)
        # ][0]
        #
        # res["audience_name"] = conditions_listofdic["audience_name"]
        # res["create_type_code"] = AudienceCreateType.Filter.value
        # res["create_type_name"] = AudienceCreateType.Filter.desc
        # res["filters"] = conditions_listofdic["conditions"]["filters"]
        # res["exclusions"] = conditions_listofdic["conditions"]["exclusions"]
        # res["upload"] = None
        # res["created_at"] = conditions_listofdic["created_at"]
        # res["updated_at"] = conditions_listofdic["updated_at"]
        #
        # return res

    def get_csv_uploaded_data(
        self, audience_id: str
    ) -> AudienceCreationOptionsResponse:
        """타겟 오디언스 csv 업로드 정보를 내려주는 함수"""

        upload_conditions = self.audience_repository.get_audience_upload_info(
            audience_id
        )
        upload_conditions = upload_conditions[0]

        upload_count = upload_conditions.upload_count
        actual_count = upload_conditions.checked_count
        template_type = upload_conditions.template_type

        result_sentence = self.csv_check_sentence_converter(
            actual_count, template_type, upload_count
        )

        return AudienceCreationOptionsResponse(
            audience_name=upload_conditions.audience_name,
            create_type_code=upload_conditions.create_type_code,
            create_type_name=upload_conditions.create_type_name,
            upload=UploadOptionResponse(
                result=result_sentence,
                type=template_type,
                upload_count=upload_count,
                checked_list=upload_conditions.checked_list,
            ),
            created_at=upload_conditions.created_at,
            updated_at=upload_conditions.updated_at,
        )

    def csv_check_sentence_converter(
        self, actual_count, template_type, upload_count, checked_shop_cnt=None
    ):
        if template_type == CsvTemplates.cus_cd.name:
            result_sentence = (
                f"{upload_count}개의 고객목록 중 {actual_count:,}개가 확인됐습니다."
            )
        elif template_type == CsvTemplates.shop_cd.name:
            result_sentence = f"{upload_count}개의 주관리 매장 중 {checked_shop_cnt:,}개가 확인되었으며, {checked_shop_cnt:,}개의 주관리 매장에 해당되는 고객번호 {actual_count:,}개가 확인되었습니다."
        else:
            raise ValueError("Invalid template type provided")
        return result_sentence
