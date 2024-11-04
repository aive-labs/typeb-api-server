from fastapi import HTTPException
from sqlalchemy import and_, except_, or_
from sqlalchemy.orm import Session
from sqlalchemy.sql.expression import Alias

from src.audiences.enums.audience_create_type import AudienceCreateType
from src.audiences.enums.audience_status import AudienceStatus
from src.audiences.enums.csv_template import CsvTemplates
from src.audiences.infra.entity import variable_table_list
from src.audiences.infra.entity.variable_table_list import CustomerInfoStatusEntity
from src.audiences.routes.dto.request.audience_update import AudienceUpdate
from src.audiences.routes.port.usecase.update_audience_usecase import (
    UpdateAudienceUseCase,
)
from src.audiences.service.port.base_audience_repository import BaseAudienceRepository
from src.audiences.utils.query_builder import (
    build_select_query,
    classify_conditions_based_on_tablename,
    execute_query_compiler,
    get_query_type_with_additional_filters,
    group_where_conditions,
)
from src.core.transactional import transactional
from src.users.domain.user import User


class UpdateAudienceService(UpdateAudienceUseCase):

    def __init__(self, audience_repository: BaseAudienceRepository):
        self.audience_repository = audience_repository

    @transactional
    def exec(self, audience_id: str, audience_update: AudienceUpdate, user: User, db: Session):

        audience = self.audience_repository.get_audience_detail(audience_id, db)
        self.check_if_audience_type_segment(audience, user)
        self.check_duplicated_name(audience_id, audience_update, db)

        # 관련 데이터 삭제
        self.audience_repository.delete_audience_info_for_update(audience_id, db)

        # audiences 수정
        create_type_code = audience_update.create_type_code
        if create_type_code == AudienceCreateType.Filter.value:
            update_audience_id = self.update_audience_by_filter(
                create_type_code, audience_id, audience_update, user, db
            )
            self.save_audience_customer_list(audience_id, user, db)
        elif create_type_code == AudienceCreateType.Upload.value:
            update_audience_id = self.update_audience_by_upload(
                create_type_code, audience_id, audience_update, user, db
            )
        else:
            raise ValueError("허용되지 않은 생성 타입 코드 입니다.")

        return update_audience_id

    def save_audience_customer_list(self, audience_id: str, user: User, db: Session):
        creation_options = self.audience_repository.get_db_filter_conditions(audience_id, db)
        print("creation_options")
        print(creation_options)
        options = creation_options[0].conditions
        print("options")
        print(options)
        query = self.get_final_query(user, options, db)
        print("query")
        print(query)

        self.audience_repository.save_audience_list(audience_id, query, db)

    def check_duplicated_name(self, audience_id, audience_update, db: Session):
        duplicated_name_audience = self.audience_repository.get_audience_by_name(
            audience_update.audience_name, db
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
        pass

    def update_audience_by_upload(
        self, create_type_code, audience_id, audience_update, user, db: Session
    ):

        template_name = audience_update.upload["type"]

        # 업로드 템플릿 식별 후 schema와 field 변수 할당
        templates_members = CsvTemplates.get_eums()
        template = next(
            (template for template in templates_members if template["_name_"] == template_name),
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
         message_template 코드(cus_cd, shop_code, ...) 에 따른 대상 cust_ids 추출
        """

        # Audience 데이터 저장
        insert_to_audiences = {
            "audience_name": audience_update.audience_name,
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
            db,
        )

        return audience_id

    def update_audience_by_filter(
        self, create_type_code, audience_id, audience_update, user, db: Session
    ):

        # 생성
        """
        생성 로직.. -> 임시 테이블에 저장
        -DB가 모두 정상적으로 업데이트 되었을 때, INSERT TO & 임시 테이블 삭제
        -DB 업데이트중 Fail 발생 시, 임시 테이블 삭제
        """

        # Audiences 저장
        insert_to_audiences = {
            "audience_name": audience_update.audience_name,
            "create_type_code": create_type_code,
            "target_strategy": audience_update.target_strategy.value,
            "updated_by": str(user.user_id),
        }

        # Audience filter conditions 저장 - 새로 생성 필요
        filters = [i.dict() for i in audience_update.filters]
        exclusions = [i.dict() for i in audience_update.exclusions]

        insert_to_filter_conditions = {
            "conditions": {"filters": filters, "exclusions": exclusions},
            "exclusion_condition": {"exclusion_condition": exclusions},
            # TODO - 설명 문장 수정 필요
            "exclusion_description": ["1샘플 수정문장입니다.", "2샘플 수정문장입니다."],
        }

        self.audience_repository.update_by_filter(
            audience_id, insert_to_filter_conditions, insert_to_audiences, db
        )

        return audience_id

    def get_final_query(self, user, filter_condition, db: Session):
        # **variable_type 반환(target / event) : 추가 필요
        # 인덱스 기준 넘버링된 조건 입력되는 딕셔너리(condition_1_1, condition_1_2, condition_2_1 ...)
        condition_dict = {}
        filter_or_exclutions_query_list = []
        # filters, exclusions 키 별로 조건들을 저장
        for set_operator in ["filters", "exclusions"]:
            and_conditions_list = filter_condition[set_operator]

            if and_conditions_list:
                condition_dict = {}
                where_condition_dict = {}
                # 전체 고객 모수 조회
                all_customer = self.audience_repository.get_all_customer_by_audience(
                    user=user, db=db
                )

                # 조건 넘버링 n1
                for n1, and_conditions in enumerate(and_conditions_list, 1):
                    n2 = 0
                    for and_condition in and_conditions["and_conditions"]:
                        query_type_dict = get_query_type_with_additional_filters(and_condition)
                        n2 += 1

                        if query_type_dict is None:
                            raise Exception()

                        # variable_type 고정 : target
                        print("query_type_dict")
                        print(query_type_dict)

                        if query_type_dict["field"] in (
                            "visit_product_name",
                            "visit_full_category_name_1",
                            "visit_full_category_name_2",
                            "visit_full_category_name_3",
                            "visit_page_title",
                        ):
                            field_with_visit_prefix = query_type_dict["field"].replace("visit_", "")
                            query_type_dict["field"] = field_with_visit_prefix

                        variable_table = self.audience_repository.get_tablename_by_variable_id(
                            query_type_dict["field"], db
                        )
                        table_name = variable_table.target_table

                        query_type_dict["table_name"] = table_name
                        condition_dict[f"condition_{n1}_{n2}"] = query_type_dict

                table_condition_dict = classify_conditions_based_on_tablename(condition_dict)

                idx = 0
                for table_name, condition_list in table_condition_dict.items():
                    # 테이블 객체 불러오기
                    variable_table = getattr(variable_table_list, table_name)

                    # 테이블별 select list 생성
                    select_query_list = []
                    array_select_query_list = []
                    for condition_name in condition_list:
                        condition = condition_dict[condition_name]
                        # 각 select line(conditoin_n1_n2)을 select list 에 append
                        temp_select_query = build_select_query(
                            variable_table, condition, condition_name
                        )

                        print("select query")
                        print(temp_select_query)
                        a = execute_query_compiler(temp_select_query[1])
                        print(a)

                        if temp_select_query is None:
                            raise Exception()

                        if temp_select_query[0]:
                            select_query_list.append(temp_select_query[1])
                        elif not temp_select_query[0]:
                            array_select_query_list.append(temp_select_query[1])

                    for temp_idx, temp_select_list in enumerate(
                        [select_query_list, array_select_query_list]
                    ):
                        print("temp_idx")
                        print(temp_idx)
                        if temp_select_list:
                            if temp_idx == 0:
                                sub_alias: Alias = (
                                    self.audience_repository.get_subquery_with_select_query_list(
                                        variable_table, select_query_list, idx, db
                                    )
                                )
                            else:
                                # temp_idx == 1
                                sub_alias: Alias = (
                                    self.audience_repository.get_subquery_with_array_select_query_list(
                                        variable_table, array_select_query_list, idx, db
                                    )
                                )

                            print("sub_alias query")
                            a = execute_query_compiler(sub_alias)
                            print(a)

                            where_condition_dict = group_where_conditions(
                                sub_alias,
                                condition_dict,
                                condition_list,
                                where_condition_dict,
                            )

                            print("where_condition_dict")
                            print(where_condition_dict)

                            all_customer = all_customer.outerjoin(  # pyright: ignore [reportAttributeAccessIssue]
                                sub_alias,
                                CustomerInfoStatusEntity.cus_cd == sub_alias.c.cus_cd,
                            )
                            idx += 1

                total_where_condition = or_(
                    *[and_(*same_n1) for same_n1 in where_condition_dict.values()]
                )
                all_customer = all_customer.filter(  # pyright: ignore [reportAttributeAccessIssue]
                    total_where_condition
                )
                filter_or_exclutions_query_list.append(all_customer)
        result = except_(*filter_or_exclutions_query_list)

        print("result select query")
        a = execute_query_compiler(result)
        print(a)
        return result
