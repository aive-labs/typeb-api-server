from fastapi import BackgroundTasks, HTTPException
from sqlalchemy import and_, except_, or_

from src.audiences.enums.audience_create_type import AudienceCreateType
from src.audiences.enums.audience_status import AudienceStatus
from src.audiences.enums.audience_type import AudienceType
from src.audiences.enums.csv_template import CsvTemplates
from src.audiences.enums.predefined_variable_access import PredefinedVariableAccess
from src.audiences.infra import entity
from src.audiences.infra.audience_repository import AudienceRepository
from src.audiences.infra.entity.customer_info_status_entity import (
    CustomerInfoStatusEntity,
)
from src.audiences.routes.dto.request.audience_create import AudienceCreate
from src.audiences.routes.port.usecase.create_audience_usecase import (
    CreateAudienceUseCase,
)

# from src.audiences.service.background.execute_target_audience_summary import (
#     execute_target_audience_summary,
# )
from src.audiences.utils.query_builder import (
    build_select_query,
    classify_conditions_based_on_tablename,
    execute_query_compiler,
    get_query_type_with_additional_filters,
    group_where_conditions,
)
from src.users.domain.user import User
from src.utils.data_converter import DataConverter


class CreateAudienceService(CreateAudienceUseCase):

    def __init__(self, audience_repository: AudienceRepository):
        self.audience_repository = audience_repository

    def create_audience(
        self,
        audience_create: AudienceCreate,
        user: User,
        background_task: BackgroundTasks,
    ):
        audience = self.audience_repository.get_audience_by_name(
            audience_create.audience_name
        )

        # 오디언스명 중복 체크
        if audience is None:
            raise HTTPException(
                status_code=409,
                detail={
                    "code": "audience/create",
                    "message": "동일한 오디언스명이 존재합니다.",
                },
            )

        if audience_create.create_type_code == AudienceCreateType.Filter.value:
            ctype = AudienceCreateType.Filter.value

            to_audiences, filter_conditions = self._create_audience_by_filter(
                ctype, audience_create, user
            )

            new_audience_id = self.audience_repository.create_audience(
                to_audiences, filter_conditions
            )

            # 타겟 오디언스 고객 리스트 저장
            audience_filter_condition = (
                self.audience_repository.get_db_filter_conditions(new_audience_id)
            )
            conditions = audience_filter_condition[0][2]
            query = self._get_final_query(user, conditions)
            execute_query_compiler(query)

            self.audience_repository.save_audience_list(new_audience_id, query)

        elif audience_create.create_type_code == AudienceCreateType.Upload.value:
            ctype = AudienceCreateType.Upload.value
            template_name = audience_create.upload["type"]  # type: ignore

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

            schema_md = template["source"]
            if not schema_md:
                raise ValueError("Invalid create typecode provided")

            template["_name_"]

            # 대상 고객 생성 로직
            """
            생성 로직..
            - 임시 테이블에 저장
            - DB가 정상적으로 업데이트되었을 때 INSERT INTO & 임시 테이블 삭제
            - DB 업데이트 중 실패 발생 시 임시 테이블 삭제
            """

            # audiences 저장 데이터 준비
            insert_to_audiences = {
                "audience_name": audience_create.audience_name,
                "audience_type_code": AudienceType.custom.value,
                "audience_type_name": AudienceType.custom.description,
                "create_type_code": ctype,
                "audience_status_code": AudienceStatus.inactive.value,
                "audience_status_name": AudienceStatus.inactive.description,
                "description": None,
                "owned_by_dept": user.department_id,
                "created_by": str(user.user_id),
                "updated_by": str(user.user_id),
            }

            # upload_condition 저장 데이터 준비
            insert_to_uploaded_audiences = {
                "template_type": audience_create.upload["type"],  # type: ignore
                "upload_count": audience_create.upload["upload_count"],  # type: ignore
                "checked_count": len(audience_create.upload["checked_list"]),  # type: ignore
                "checked_list": audience_create.upload["checked_list"],  # type: ignore
            }

            upload_check_list = audience_create.upload["check_list"]  # type: ignore
            new_audience_id = self.audience_repository.create_audience_by_upload(
                insert_to_audiences, insert_to_uploaded_audiences, upload_check_list
            )
        else:
            raise ValueError("Invalid create typecode provided")

        # background_task.add_task(execute_target_audience_summary, new_audience_id)
        return new_audience_id

    def _get_final_query(self, user, filter_condition):
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
                    user=user
                )

                # 조건 넘버링 n1
                for n1, and_conditions in enumerate(and_conditions_list, 1):
                    n2 = 0
                    for and_condition in and_conditions["and_conditions"]:
                        query_type_dict = get_query_type_with_additional_filters(
                            and_condition
                        )
                        n2 += 1

                        if query_type_dict is None:
                            raise Exception()

                        # variable_type 고정 : target
                        table_name = (
                            self.audience_repository.get_tablename_by_variable_id(
                                query_type_dict["field"]
                            )
                        )
                        if table_name is None:
                            raise Exception()

                        query_type_dict["table_name"] = table_name
                        condition_dict[f"condition_{n1}_{n2}"] = query_type_dict

                table_condition_dict = classify_conditions_based_on_tablename(
                    condition_dict
                )

                idx = 0
                for table_name, condition_list in table_condition_dict.items():
                    # 테이블 객체 불러오기
                    variable_table = getattr(entity, table_name)

                    # 테이블별 select list 생성
                    select_query_list = []
                    array_select_query_list = []
                    for condition_name in condition_list:
                        condition = condition_dict[condition_name]
                        # 각 select line(conditoin_n1_n2)을 select list 에 append
                        temp_select_query = build_select_query(
                            variable_table, condition, condition_name
                        )

                        if temp_select_query is None:
                            raise Exception()

                        if temp_select_query[0]:
                            select_query_list.append(temp_select_query[1])
                        elif not temp_select_query[0]:
                            array_select_query_list.append(temp_select_query[1])

                    for temp_idx, temp_select_list in enumerate(
                        [select_query_list, array_select_query_list]
                    ):
                        if temp_select_list:
                            if temp_idx == 0:
                                sub_alias = self.audience_repository.get_subquery_with_select_query_list(
                                    variable_table, select_query_list, idx
                                )
                            else:
                                # temp_idx == 1
                                sub_alias = self.audience_repository.get_subquery_with_array_select_query_list(
                                    variable_table, array_select_query_list, idx
                                )
                            where_condition_dict = group_where_conditions(
                                sub_alias,
                                condition_dict,
                                condition_list,
                                where_condition_dict,
                            )
                            all_customer = all_customer.outerjoin(
                                sub_alias,
                                CustomerInfoStatusEntity.cus_cd == sub_alias.c.cus_cd,
                            )
                            idx += 1

                total_where_condition = or_(
                    *[and_(*same_n1) for same_n1 in where_condition_dict.values()]
                )
                all_customer = all_customer.filter(total_where_condition)
                filter_or_exclutions_query_list.append(all_customer)
        result = except_(*filter_or_exclutions_query_list)
        return result

    def _create_audience_by_filter(
        self, ctype: str, audience_create: AudienceCreate, user: User
    ):
        insert_to_audiences = {}
        insert_to_audiences["audience_name"] = audience_create.audience_name
        insert_to_audiences["audience_type_code"] = AudienceType.custom.value
        insert_to_audiences["audience_type_name"] = AudienceType.custom.description
        insert_to_audiences["create_type_code"] = ctype
        insert_to_audiences["audience_status_code"] = AudienceStatus.inactive.value
        insert_to_audiences["audience_status_name"] = (
            AudienceStatus.inactive.description
        )
        insert_to_audiences["user_exc_deletable"] = (
            True  # 제외오디언스 파란색 표시 -True
        )
        insert_to_audiences["description"] = None
        insert_to_audiences["owned_by_dept"] = user.department_id
        insert_to_audiences["created_by"] = str(user.user_id)
        insert_to_audiences["updated_by"] = str(user.user_id)

        # audience_filter_conditions 저장 - 새로 생성 필요
        insert_to_filter_conditions = {}

        filters = []
        if audience_create.filters is not None:
            filters = [i.model_dump() for i in audience_create.filters]

        exclusions = []
        if audience_create.exclusions is not None:
            exclusions = [i.model_dump() for i in audience_create.exclusions]

        insert_to_filter_conditions["conditions"] = {
            "filters": filters,
            "exclusions": exclusions,
        }
        insert_to_filter_conditions["exclusion_condition"] = {
            "exclusion_condition": exclusions
        }
        insert_to_filter_conditions["exclusion_description"] = [
            "1샘플문장입니다.",
            "2샘플문장입니다.",
        ]

        return insert_to_audiences, insert_to_filter_conditions

    def get_audience_variable_combinations(self, user: User) -> list[dict]:
        access_lv = [
            level.value
            for level in PredefinedVariableAccess
            if level.name == user.role_id
        ][0]

        variable_combinations = self.audience_repository.get_variable_options(access_lv)

        variables_combination_list = DataConverter.convert_query_to_list(
            variable_combinations
        )

        for item in variables_combination_list:
            item["additional_variable"] = tuple(item["additional_variable"])

        group_bys = [
            "variable_id",
            "variable_name",
            "variable_group_code",
            "variable_group_name",
            "combination_type",
            "additional_variable",
        ]

        # Group by the specified keys
        grouped_variables = {}
        for item in variables_combination_list:
            key = tuple(item[col] for col in group_bys)
            if key not in grouped_variables:
                grouped_variables[key] = []
            grouped_variables[key].append(item)

        options_by_cell = []
        for key, group in grouped_variables.items():
            predefined_elem = {
                "variable_id": key[0],
                "variable_name": key[1],
                "variable_group_code": key[2],
                "variable_group_name": key[3],
                "combination_type": key[4],
                "additional_variable": key[5],
                "combinations": [],
            }

            # Sorting and removing duplicates based on 'component_order_cols'
            sub_groups = sorted(
                {
                    tuple(
                        g[col]
                        for col in [
                            "data_type",
                            "data_type_desc",
                            "cell_type",
                            "component_order_cols",
                        ]
                    )
                    for g in group
                },
                key=lambda x: x[3],
            )

            for cell in sub_groups:
                combination_elem = {}
                if cell[2] in ["datepicker"]:
                    combination_elem["data_type"] = None
                    combination_elem["data_type_desc"] = None
                    combination_elem["cell_type"] = cell[2]
                else:
                    combination_elem["data_type"] = cell[0]
                    combination_elem["data_type_desc"] = cell[1]
                    combination_elem["cell_type"] = cell[2]
                predefined_elem["combinations"].append(combination_elem)

            # Add input_cell_type if it exists
            input_cells = {g["input_cell_type"] for g in group}
            if input_cells:
                input_cell_type = {
                    "cell_type": input_cells.pop(),
                    "data_type": None,
                    "values": None,
                }
                predefined_elem["combinations"].append(input_cell_type)

            options_by_cell.append(predefined_elem)

        return options_by_cell
