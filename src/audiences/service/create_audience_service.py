from collections import defaultdict

from sqlalchemy import and_, except_, or_
from sqlalchemy.orm import Session
from sqlalchemy.sql.expression import Alias

from src.audiences.enums.audience_create_type import AudienceCreateType
from src.audiences.enums.audience_status import AudienceStatus
from src.audiences.enums.csv_template import CsvTemplates
from src.audiences.enums.predefined_variable_access import PredefinedVariableAccess
from src.audiences.infra.audience_repository import AudienceRepository
from src.audiences.infra.entity import variable_table_list
from src.audiences.infra.entity.variable_table_list import CustomerInfoStatusEntity
from src.audiences.routes.dto.request.audience_create import AudienceCreate
from src.audiences.routes.dto.response.audience_variable_combinations import (
    DataType,
    Option,
    PredefinedVariable,
)
from src.audiences.routes.dto.response.target_strategy_combination import (
    TargetStrategyAndCondition,
    TargetStrategyCombination,
    TargetStrategyCondition,
    TargetStrategyFilter,
    TargetStrategyFilterWrapping,
)
from src.audiences.routes.port.usecase.create_audience_usecase import (
    CreateAudienceUseCase,
)
from src.audiences.utils.query_builder import (
    build_select_query,
    classify_conditions_based_on_tablename,
    execute_query_compiler,
    get_query_type_with_additional_filters,
    group_where_conditions,
)
from src.core.exceptions.exceptions import DuplicatedException
from src.core.transactional import transactional
from src.users.domain.user import User


class CreateAudienceService(CreateAudienceUseCase):

    def __init__(self, audience_repository: AudienceRepository):
        self.audience_repository = audience_repository

    @transactional
    def create_audience(self, audience_create: AudienceCreate, user: User, db: Session):
        audience = self.audience_repository.get_audience_by_name(audience_create.audience_name, db)

        # 오디언스명 중복 체크
        if audience:
            raise DuplicatedException(detail={"message": "동일한 오디언스명이 존재합니다."})

        if audience_create.create_type_code == AudienceCreateType.Filter.value:
            ctype = AudienceCreateType.Filter.value

            to_audiences, filter_conditions = self._create_audience_by_filter(
                ctype, audience_create, user, db
            )

            new_audience_id = self.audience_repository.create_audience(
                to_audiences, filter_conditions, db
            )

            # 타겟 오디언스 고객 리스트 저장
            audience_filter_condition = self.audience_repository.get_db_filter_conditions(
                new_audience_id, db
            )
            conditions = audience_filter_condition[0].conditions
            print("conditions")
            print(conditions)
            query = self.get_final_query(user, conditions, db)
            execute_query_compiler(query)
            print("query")
            print(query)

            self.audience_repository.save_audience_list(new_audience_id, query, db)

        elif audience_create.create_type_code == AudienceCreateType.Upload.value:
            create_type_code = AudienceCreateType.Upload.value
            template_name = audience_create.upload["type"]  # type: ignore

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
                "create_type_code": create_type_code,
                "target_strategy": audience_create.target_strategy.value,
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
                insert_to_audiences, insert_to_uploaded_audiences, upload_check_list, db
            )
        else:
            raise ValueError("타겟 오디언스 생성 미지원 타입입니다.")

        return new_audience_id

    def _create_audience_by_filter(
        self, ctype: str, audience_create: AudienceCreate, user: User, db: Session
    ):
        insert_to_audiences = {}
        insert_to_audiences["audience_name"] = audience_create.audience_name
        insert_to_audiences["create_type_code"] = ctype
        insert_to_audiences["audience_status_code"] = AudienceStatus.inactive.value
        insert_to_audiences["target_strategy"] = audience_create.target_strategy.value
        insert_to_audiences["audience_status_name"] = AudienceStatus.inactive.description
        insert_to_audiences["user_exc_deletable"] = True  # 제외오디언스 파란색 표시 -True
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
        insert_to_filter_conditions["exclusion_condition"] = {"exclusion_condition": exclusions}
        insert_to_filter_conditions["exclusion_description"] = [
            "1샘플문장입니다.",
            "2샘플문장입니다.",
        ]

        return insert_to_audiences, insert_to_filter_conditions

    def get_audience_target_strategy_combinations(self, db: Session) -> TargetStrategyCombination:

        new_customer_guide = TargetStrategyAndCondition(
            no=0,
            conditions=[
                TargetStrategyCondition(
                    value="NEW_CUSTOMER,INACTIVE_NEW_M1,INACTIVE_NEW_M3,INACTIVE_NEW_M6,INACTIVE_NEW_M9",
                    cell_type="multi_select",
                    data_type="d_cv",
                )
            ],
            variable_id="cv_model",
            additional_filters=None,
        )
        new_customer_guide = TargetStrategyFilterWrapping(
            filter=TargetStrategyFilter(and_conditions=[new_customer_guide])
        )

        engagement_customer = TargetStrategyAndCondition(
            no=0,
            conditions=[
                TargetStrategyCondition(
                    value="ACTIVE_CUSTOMER1,ACTIVE_CUSTOMER2,ACTIVE_CUSTOMER3,ACTIVE_CUSTOMER4,INACTIVE_ACT1_M3,INACTIVE_ACT1_M6,INACTIVE_ACT1_M9,INACTIVE_ACT2_M3,INACTIVE_ACT2_M6,INACTIVE_ACT2_M9,INACTIVE_ACT3_M3,INACTIVE_ACT3_M6,INACTIVE_ACT3_M9",
                    cell_type="multi_select",
                    data_type="d_cv",
                )
            ],
            variable_id="cv_model",
            additional_filters=None,
        )
        engagement_customer = TargetStrategyFilterWrapping(
            filter=TargetStrategyFilter(and_conditions=[engagement_customer])
        )

        loyal_customer_management = TargetStrategyAndCondition(
            no=0,
            conditions=[
                TargetStrategyCondition(
                    value="INACTIVE_ACT4_M3,INACTIVE_ACT4_M6,INACTIVE_ACT4_M9",
                    cell_type="multi_select",
                    data_type="d_cv",
                )
            ],
            variable_id="cv_model",
            additional_filters=None,
        )
        loyal_customer_management = TargetStrategyFilterWrapping(
            filter=TargetStrategyFilter(and_conditions=[loyal_customer_management])
        )

        preventing_customer_churn = TargetStrategyAndCondition(
            no=0,
            conditions=[
                TargetStrategyCondition(
                    value="INACTIVE_ACT1_M9,INACTIVE_ACT2_M9,INACTIVE_ACT3_M9,INACTIVE_ACT4_M9",
                    cell_type="multi_select",
                    data_type="d_cv",
                )
            ],
            variable_id="cv_model",
            additional_filters=None,
        )
        preventing_customer_churn = TargetStrategyFilterWrapping(
            filter=TargetStrategyFilter(and_conditions=[preventing_customer_churn])
        )

        reactivate_customer = TargetStrategyAndCondition(
            no=0,
            conditions=[
                TargetStrategyCondition(
                    value="CHURN_M12,CHURN_M18,CHURN_M24,CHURN_M30",
                    cell_type="multi_select",
                    data_type="d_cv",
                )
            ],
            variable_id="cv_model",
            additional_filters=None,
        )
        reactivate_customer = TargetStrategyFilterWrapping(
            filter=TargetStrategyFilter(and_conditions=[reactivate_customer])
        )

        return TargetStrategyCombination(
            new_customer_guide=new_customer_guide,
            engagement_customer=engagement_customer,
            loyal_customer_management=loyal_customer_management,
            preventing_customer_churn=preventing_customer_churn,
            reactivate_customer=reactivate_customer,
        )

    def get_audience_variable_combinations(
        self, user: User, db: Session
    ) -> list[PredefinedVariable]:
        access_lv = [
            level.value for level in PredefinedVariableAccess if level.name == user.role_id
        ][0]

        variables_combi_df = self.audience_repository.get_variable_options(access_lv, db)

        variables_combi_df["additional_variable"] = variables_combi_df["additional_variable"].apply(
            tuple
        )

        group_bys = [
            "variable_id",
            "variable_name",
            "variable_group_code",
            "variable_group_name",
            "combination_type",
            "additional_variable",
        ]

        options_by_cell = []
        for key, group in variables_combi_df.groupby(group_bys):

            if not isinstance(key, tuple):
                # groupby 메서드를 사용할 때 key는 그룹화된 값들을 나타내며, 단일 값이거나 튜플일 수 있음
                # 타입이 튜플인지 확인이 필요함
                raise Exception("데이터 확인이 필요합니다.")

            predefined_variable = PredefinedVariable(
                variable_id=key[0],
                variable_name=key[1],
                variable_group_code=key[2],
                variable_group_name=key[3],
                combination_type=key[4],
                additional_variable=key[5],
                combinations=[],
            )

            combinations = self._create_combinations(group)
            predefined_variable.combinations = combinations
            options_by_cell.append(predefined_variable)

        return options_by_cell

    def _create_combinations(self, group):

        sub_groups = (  # pyright: ignore [reportCallIssue]
            group.reset_index(drop=True)[
                (["data_type", "data_type_desc", "cell_type", "component_order_cols"])
            ]
            .drop_duplicates()
            .sort_values("component_order_cols")
        )

        combinations = []
        # for cell, sub_group in sub_groups:
        for cell in zip(
            sub_groups["data_type"],
            sub_groups["data_type_desc"],
            sub_groups["cell_type"],
        ):
            combi_elem = {}
            if cell[2] in ["datepicker"]:
                combi_elem["data_type"] = None
                combi_elem["data_type_desc"] = None
                combi_elem["cell_type"] = cell[2]
            else:
                combi_elem["data_type"] = cell[0]
                combi_elem["data_type_desc"] = cell[1]
                combi_elem["cell_type"] = cell[2]
            combinations.append(combi_elem)
        if input_cell := group["input_cell_type"].unique()[0]:
            input_cell_type = {
                "cell_type": input_cell,
                "data_type": None,
                "values": None,
            }
            combinations.append(input_cell_type)
        return combinations

    def get_option_items(self, db: Session) -> list[DataType]:
        """data_type별로 옵션 name과 input_type을 내려주는 함수"""

        options = self.audience_repository.get_options(db)

        options_dict = [row._asdict() for row in options]

        added_dict = defaultdict(list)

        for item in options_dict:
            key_field_val = item["data_type"]
            if item.get("option_id") is not None:
                added_dict[key_field_val].append(
                    Option(
                        id=item["option_id"],
                        name=item["option_name"],
                        input_cell_type=item["input_cell_type"],
                    )
                )
            else:
                added_dict[key_field_val].append(None)

        data_type_list = [
            DataType(data_type=key, options=value) for key, value in added_dict.items()
        ]
        return data_type_list

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
