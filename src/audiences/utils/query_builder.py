from sqlalchemy import and_, case, distinct, func, not_

from src.audiences.infra.entity.customer_promotion_master_entity import (
    CustomerPromotionMasterEntity,
)
from src.audiences.infra.entity.customer_promotion_react_summary_entity import (
    CustomerPromotionReactSummaryEntity,
)
from src.audiences.infra.entity.purchase_analytics_master_style_entity import (
    PurchaseAnalyticsMasterStyle,
)
from src.audiences.infra.entity.variable_table_list import (
    CustomerInfoStatusEntity,
    CustomerProductPurchaseSummaryEntity,
    GaViewMasterEntity,
)
from src.core.exceptions.exceptions import ConsistencyException, ValidationException


def set_query_type_lv2(and_condition):
    result = {
        "field": and_condition["variable_id"],
        "data": convert_date_value_format(
            and_condition["conditions"][0]["value"],
            and_condition["conditions"][0]["cell_type"],
        ),
    }
    return result


def set_query_type_lv3(and_condition):
    result = {
        "field": and_condition["variable_id"],
        "condition": and_condition["conditions"][0]["value"],
        "data": convert_date_value_format(
            and_condition["conditions"][1]["value"],
            and_condition["conditions"][1]["cell_type"],
        ),
    }
    return result


def convert_date_value_format(data, cell_type):
    if cell_type == "date_range_picker":
        data = data.split(",")
    return data


def set_query_type_lv4(and_condition):
    result = {
        "field": and_condition["variable_id"],
        "period": convert_date_value_format(
            and_condition["conditions"][0]["value"],
            and_condition["conditions"][0]["cell_type"],
        ),
        "condition": and_condition["conditions"][1]["value"],
        "data": and_condition["conditions"][2]["value"],
    }
    return result


def delete_event_field_check(field):
    return field[2:] if field.startswith("e_") else field


def get_query_type(and_condition):
    print("and_condition")
    print(and_condition)
    comb_lv = len(and_condition["conditions"]) + 1
    if comb_lv == 2:
        return set_query_type_lv2(and_condition)
    elif comb_lv == 3:
        return set_query_type_lv3(and_condition)
    elif comb_lv == 4:
        return set_query_type_lv4(and_condition)
    else:
        raise ValidationException(detail={"message": "필터는 최소 1개 이상 선택해야합니다."})


def get_query_type_with_additional_filters(and_condition):
    result = get_query_type(and_condition)
    if and_condition["variable_id"] in (["recency", "e_recency"]):
        result["period"] = "2y"
        result["field"] = delete_event_field_check(result["field"])
    if and_condition.get("additional_filters"):
        result["additional_filters"] = [
            get_query_type(additional_condition)
            for additional_condition in and_condition["additional_filters"]
        ]
    return result


def classify_conditions_based_on_tablename(condition_dict):
    """
    테이블 명에 따라 조건을 분류하는 함수 : 동일한 테이블을 사용하는 항목을 한 번에 조회하기 위함
    """
    table_condition_dict = {}

    for key, value in condition_dict.items():
        temp_table_name = value["table_name"]
        table_condition_dict[temp_table_name] = table_condition_dict.get(temp_table_name, []) + [
            key
        ]

    return table_condition_dict


def apply_calculate_method(table_obj, query_list, field_list, condition_name, agg_variable_name):
    """
    변수(field)에 따라 집계 방법을 적용하는 함수
    """
    if table_obj == CustomerInfoStatusEntity:
        return (True, query_list[0].label(condition_name))
    elif table_obj in (
        CustomerProductPurchaseSummaryEntity,
        PurchaseAnalyticsMasterStyle,
    ):
        if field_list[0].startswith(("sale_amt", "sale_qty", "milege_usage")):
            return (True, func.sum(query_list[0]).label(condition_name))
        elif field_list[0].startswith("sale_dt"):
            return (
                False,
                func.unnest(query_list[0]).label(condition_name + f"_{agg_variable_name}"),
            )
    elif table_obj in (
        CustomerPromotionReactSummaryEntity,
        CustomerPromotionMasterEntity,
    ):
        if len(query_list) == 1:
            return (True, func.sum(query_list[0]).label(condition_name))
        else:
            return (
                True,
                (func.sum(query_list[0]) / func.sum(query_list[1])).label(condition_name),
            )
    elif table_obj == GaViewMasterEntity:
        print("create_ga_subquery")
        if field_list[0].startswith("visit_dt"):
            return (True, func.count(distinct(query_list[0])).label(condition_name))
        elif field_list[0].startswith("product_name"):
            return (True, query_list[0].label(condition_name))
    else:
        return (True, query_list[0].label(condition_name))


def build_select_query(table_obj, condition, condition_name):
    """
    TABLE 객체와 condition을 입력받았을 때 select 쿼리를 추출하는 함수
    """
    additional_filters = condition.get("additional_filters")

    field = condition["field"]
    print(f"field: {field}")
    field_list = []

    # 이벤트 변수이거나 행동 데이터이거나
    if is_event_variable := field.startswith("e_"):
        field = delete_event_field_check(field)

    if is_action_variable := field.startswith("visit_count"):
        field = "visit_dt"
        print("action field")
        print(field)

    if field.startswith(("freq", "recency", "purcycle")):
        field_list = ["sale_dt_array"]

    elif field.endswith("ratio"):
        if field.startswith("response"):
            field_list = ["response_cnt", "send_cnt"]
        elif field.startswith("use_offer"):
            field_list = ["use_offer_cnt", "recommend_cnt"]
        elif field.startswith("recommend_purchase"):
            field_list = ["recommend_purchase_cnt", "recommend_cnt"]
    else:
        field_list = [field]

    select_query_list = []
    and_conditions_in_case = []

    for field in field_list:
        if period := condition.get("period"):
            if is_event_variable:
                dt_column = "sale_dt" if table_obj == PurchaseAnalyticsMasterStyle else "send_dt"
                and_conditions_in_case.append(
                    and_(getattr(table_obj, dt_column).between(period[0], period[1]))
                )
            elif is_action_variable:
                dt_column = "visit_dt"
                if table_obj != GaViewMasterEntity:
                    raise ConsistencyException(
                        detail={
                            "message": "타겟 오디언스 생성 중 오류가 발생했습니다.",
                            "error": "table_obj != GaViewMasterEntity",
                        }
                    )
                and_conditions_in_case.append(
                    and_(getattr(table_obj, dt_column).between(period[0], period[1]))
                )
            else:
                field = field + "_" + period

        if additional_filters:
            and_conditions_in_case.append(
                and_(
                    *[
                        getattr(
                            table_obj,
                            delete_event_field_check(each_additional_filter["field"]),
                        ).in_(each_additional_filter["data"].split(","))
                        for each_additional_filter in additional_filters
                    ]
                )
            )

        if and_conditions_in_case:
            print("and_conditions_in_case")
            print(table_obj)
            print(field)
            select_query = case(  # pyright: ignore [reportCallIssue]
                (
                    and_(*and_conditions_in_case),
                    getattr(table_obj, field),
                )  # pyright: ignore [reportArgumentType]
            )
        else:
            print("else")
            print(field)
            print(table_obj)
            select_query = getattr(table_obj, field)
            print(select_query)
        select_query_list.append(select_query)

    apply_calculate_method_query = apply_calculate_method(
        table_obj, select_query_list, field_list, condition_name, condition["field"]
    )
    return apply_calculate_method_query


def get_comparison_operator(fliter_column, condition, value):
    if condition == "eq":
        return [fliter_column == value]
    elif condition == "gt":
        return [fliter_column >= value]
    elif condition == "ls":
        return [fliter_column <= value]
    elif condition == "in" or condition is None:
        return [fliter_column.in_(value.split(","))]
    elif condition == "notin":
        return [not_(fliter_column.in_(value.split(",")))]


def group_where_conditions(sub_alias, condition_dict, condition_list, where_condition_dict):
    """
    where 조건 생성 함수
    동일한 n1을 갖는 where조건을 하나의 리스트로 관리
    """
    for condition_name in condition_list:
        temp_condition = condition_dict[condition_name]
        n1 = condition_name.split("_")[1]

        fliter_column = getattr(sub_alias.c, condition_name)
        condition = temp_condition.get("condition", None)
        value = temp_condition["data"]
        where_condition_dict[n1] = where_condition_dict.get(n1, []) + get_comparison_operator(
            fliter_column, condition, value
        )

    return where_condition_dict


def execute_query_compiler(query):
    """
    쿼리 객체 컴파일 함수
    """
    return query.compile(compile_kwargs={"literal_binds": True})
