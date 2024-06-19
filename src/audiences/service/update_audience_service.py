from fastapi import HTTPException

from src.audiences.enums.audience_create_type import AudienceCreateType
from src.audiences.enums.audience_status import AudienceStatus
from src.audiences.enums.audience_type import AudienceType
from src.audiences.enums.csv_template import CsvTemplates
from src.audiences.routes.dto.request.audience_update import AudienceUpdate
from src.audiences.routes.port.usecase.update_audience_usecase import (
    UpdateAudienceUseCase,
)
from src.audiences.service.port.base_audience_repository import BaseAudienceRepository
from src.users.domain.user import User


class UpdateAudienceService(UpdateAudienceUseCase):

    def __init__(self, audience_repository: BaseAudienceRepository):
        self.audience_repository = audience_repository

    def exec(self, audience_id: str, audience_update: AudienceUpdate, user: User):

        audience = self.audience_repository.get_audience_detail(audience_id)
        self.check_if_audience_type_segment(audience, user)
        self.check_duplicated_name(audience_id, audience_update)

        # 관련 데이터 삭제
        self.audience_repository.delete_audience_info_for_update(audience_id)

        # audiences 수정
        create_type_code = audience_update.create_type_code
        if create_type_code == AudienceCreateType.Filter.value:
            self.update_audience_by_filter(
                create_type_code, audience_id, audience_update, user
            ).update_audience_by_filter(
                user, create_type_code, audience_id, audience_update
            )
            self.save_audience_customer_list(audience_id, user)
        elif create_type_code == AudienceCreateType.Upload.value:
            self.update_audience_by_upload(
                create_type_code, audience_id, audience_update, user
            )
        else:
            raise ValueError("허용되지 않은 생성 타입 코드 입니다.")

        # background_task.add_task(execute_target_audience_summary, db, res)

    def save_audience_customer_list(self, audience_id: str, user: User):
        pass
        # creation_options = self.audience_repository.get_db_filter_conditions(
        #     audience_id
        # )
        # options = creation_options[0].conditions
        # query = get_final_query(user, options)
        # compiled_query = execute_query_compiler(query)
        #
        # self.audience_repository.save_audience_list(audience_id)

    def check_duplicated_name(self, audience_id, audience_update):
        duplicated_name_audience = self.audience_repository.get_audience_by_name(
            audience_update.audience_name
        )
        if duplicated_name_audience:
            if duplicated_name_audience.audience_id != audience_id:
                raise HTTPException(
                    status_code=500,
                    detail={
                        "code": "audience/create",
                        "message": "동일한 오디언스명이 존재합니다.",
                    },
                )

    def check_if_audience_type_segment(self, audience, user):
        if audience.audience_type_code == AudienceType.segment.value:
            if not user.is_admin():
                raise HTTPException(
                    status_code=500,
                    detail={
                        "code": "modify/02",
                        "message": "수정 불가 - 세그먼트 타겟입니다.",
                    },
                )

    def update_audience_by_upload(
        self, create_type_code, audience_id, audience_update, user
    ):

        template_name = audience_update.upload["type"]

        # 업로드 템플릿 식별 후 schema와 field 변수 할당
        templates_members = CsvTemplates.get_eums()
        template = next(
            (
                template
                for template in templates_members
                if template["_name_"] == template_name
            ),
            None,
        )

        if not template:
            raise ValueError("Invalid create typecode provided")

        entity = template["source"]
        if not entity:
            raise ValueError("Invalid create typecode provided")

        # 대상 고객 생성
        """
        생성 로직.. -> 임시 테이블에 저장
        -DB가 모두 정상적으로 업데이트 되었을 때, INSERT TO & 임시 테이블 삭제
        -DB 업데이트중 Fail 발생 시, 임시 테이블 삭제
         template 코드(cus_cd, shop_code, ...) 에 따른 대상 cust_ids 추출
        """

        # Audience 데이터 저장
        insert_to_audiences = {
            "audience_name": audience_update.audience_name,
            "audience_type_code": AudienceType.custom.value,
            "audience_type_name": AudienceType.custom.description,
            "create_type_code": create_type_code,
            "audience_status_code": AudienceStatus.inactive.value,
            "audience_status_name": AudienceStatus.inactive.description,
            "updated_by": str(user.user_id),
            "updated_at": audience_update.updated_at,
            "description": None,
        }

        # Uploaded Audience 데이터 저장
        insert_to_uploaded_audiences = {
            "template_type": audience_update.upload["type"],
            "upload_count": audience_update.upload["upload_count"],
            "checked_count": len(audience_update.upload["checked_list"]),
            "checked_list": audience_update.upload["checked_list"],
            "audience_id": audience_id,
        }

        # Filter 조건
        filter_audience = {"audience_id": audience_id}
        checked_list = audience_update.upload["checked_list"]

        self.audience_repository.update_by_upload(
            filter_audience,
            insert_to_uploaded_audiences,
            insert_to_audiences,
            checked_list,
        )

        return audience_id

    def update_audience_by_filter(
        self, create_type_code, audience_id, audience_update, user
    ):

        # # 생성
        # """
        # 생성 로직.. -> 임시 테이블에 저장
        # -DB가 모두 정상적으로 업데이트 되었을 때, INSERT TO & 임시 테이블 삭제
        # -DB 업데이트중 Fail 발생 시, 임시 테이블 삭제
        # """
        #
        # # Audiences 저장
        # insert_to_audiences = {
        #     "audience_name": audience_update.audience_name,
        #     "create_type_code": create_type_code,
        #     "updated_by": str(user.user_id),
        #     "updated_at": audience_update.updated_at,
        # }
        #
        # # Audience filter conditions 저장 - 새로 생성 필요
        # filters = [i.dict() for i in audience_update.filters]
        # exclusions = [i.dict() for i in audience_update.exclusions]
        #
        # insert_to_filter_conditions = {
        #     "conditions": {"filters": filters, "exclusions": exclusions},
        #     "exclusion_condition": {"exclusion_condition": exclusions},
        #     # TODO - 설명 문장 수정 필요
        #     "exclusion_description": ["1샘플 수정문장입니다.", "2샘플 수정문장입니다."],
        #     "updated_at": audience_update.updated_at,
        # }
        #
        # # Filter 조건
        # filter_audience = {"audience_id": audience_id}
        #
        # self.audience_repository.update_by_filter(
        #     audience_id, insert_to_filter_conditions, insert_to_audiences
        # )
        #
        # try:
        #
        #     # audiences
        #     db.query(schema.Audience).filter_by(**filter_audience).update(
        #         insert_to_audiences
        #     )
        #
        #     # # #audience_filter_conditions
        #     stt = db.query(schema.AudienceQueries).filter_by(**filter_audience).first()
        #     if stt:
        #         db.query(schema.AudienceQueries).filter_by(**filter_audience).update(
        #             insert_to_filter_conditions
        #         )
        #     else:
        #         insert_to_filter_conditions["audience_id"] = audience_id
        #         db.add(schema.AudienceQueries(**insert_to_filter_conditions))
        #
        #     db.commit()
        #
        # except Exception:
        #     db.rollback()
        #     raise HTTPException(status_code=400, detail="audience creation failed")
        #
        # finally:
        #     db.close()

        return audience_id
