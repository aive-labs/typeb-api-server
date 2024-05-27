from collections import defaultdict

import pandas as pd
from sqlalchemy.inspection import inspect

from src.audiences.infra.dto.audience_info import AudienceInfo


class DataConverter:

    @staticmethod
    def pydantic_to_df(audiences: list[AudienceInfo]) -> pd.DataFrame:
        """
        Pydantic 모델을 DataFrame으로 변환
        """
        audiences_dict = [audience.model_dump() for audience in audiences]
        df = pd.DataFrame(audiences_dict)

        return df

    @staticmethod
    def convert_query_to_df(orm_stt):
        """
        query object 1개를 dataframe으로 변환
        """
        return pd.read_sql(orm_stt.statement, orm_stt.session.bind)

    @staticmethod
    def convert_queries_to_df(*queries):
        """
        2개 이상의 query object를 dataframe으로 변환. 중복 허용 union
        """
        return pd.concat(
            [
                pd.read_sql(orm_stt.statement, orm_stt.session.bind)
                for orm_stt in queries
            ]
        )

    @staticmethod
    def conv_filter_obj(df, cols):
        """
        filter object 값으로 변환 함수. 중복 제거
        """
        df_m = df[cols]
        return {col: list(df_m[col].unique()) for col in df_m.columns}

    @staticmethod
    def group_vals_by_key(orm_stt, key_col, val_col):
        """
        list object 값으로 변환 함수
        key 컬럼에 대한 field value를 리스트에 원소로 저장
        """
        result = defaultdict(set)

        for query_obj in orm_stt:
            key = getattr(query_obj, key_col)
            val = getattr(query_obj, val_col)
            result[key].add(val)

        return [{key_col: k, val_col: v} for k, v in result.items()]

    @staticmethod
    def merge_dict_by_key(base_dict, added_dict, key_field: str):
        """
        key 컬럼과 매핑하여 전처리된 added_dict 리스트를 병합하는 함수
        """
        merged_data = {
            item[key_field]: {
                **item,
                **next((x for x in added_dict if x[key_field] == item[key_field]), {}),
            }
            for item in base_dict
        }

        merged_data = list(merged_data.values())

        return merged_data

    @staticmethod
    def convert_model_to_dict(model):
        """SQLAlchemy model을 dict로 변환하는 함수"""
        return {
            c.key: getattr(model, c.key) for c in inspect(model).mapper.column_attrs
        }

    @staticmethod
    def iditems_group_conv_by_key(
        listofdict: list,
        key_field: str,
        items_group_name: str,
        code_field: str,
        name_field: str,
    ):
        """
        List[Dict] 자료구조로부터 key_field 별 str:List[Dict] 자료구조를 변환하는 함수
        items_group_name의 value값은 List[Dict] 자료구조로 변환되고, CodeItems 스키마가 적용됩니다.
        """
        added_dict = defaultdict(list)

        for item in listofdict:
            key_field_val = item[key_field]
            if item.get(code_field) is not None:
                added_dict[key_field_val].append(
                    {"id": item[code_field], "name": item[name_field]}
                )
            else:
                added_dict[key_field_val].append(None)

        res_dict = [
            {key_field: key, items_group_name: value if value[0] is not None else None}
            for key, value in added_dict.items()
        ]

        return res_dict
