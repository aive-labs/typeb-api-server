from pydantic import BaseModel

from src.common.utils.data_converter import DataConverter


class FilterColumns(BaseModel):
    campaign: dict = {
        "audience_type": ["audience_type_code", "audience_type_name"],
        "rep_list": ["main_product_id", "main_product_name"],
    }

    strategy_manager: dict = {
        "audience_type": ["audience_type_code", "audience_type_name"],
        "rep_list": ["main_product_id", "main_product_name"],
    }

    target_audience: dict = {
        "rep_list": ["main_product_id", "main_product_name"],
        "owned_by_dept_list": ["owned_by_dept", "owned_by_dept_abb_name"],
    }

    contents_manager: dict = {
        "audience_type": ["audience_type_code", "audience_type_name"],
        "rep_list": ["main_product_id", "main_product_name"],
    }

    contents_library: dict = {
        "audience_type": ["audience_type_code", "audience_type_name"],
        "rep_list": ["main_product_id", "main_product_name"],
    }


class FilterProcessing:
    def __init__(self, main_view: str) -> None:
        """
        필터 목록 > 타겟 오디언스 뿐만아니라, 캠페인/전략/콘텐츠
        """
        self.main_view = main_view

    def get_filter_attribute(self):
        main_view = self.main_view
        filter_columns = FilterColumns()

        if main_view == "campaign":
            return filter_columns.campaign
        elif main_view == "strategy_manager":
            return filter_columns.strategy_manager
        elif main_view == "target_audience":
            return filter_columns.target_audience
        elif main_view == "contents_manager":
            return filter_columns.contents_manager
        elif main_view == "contents_library":
            return filter_columns.contents_library
        else:
            return None

    def filter_converter(self, df):
        filter_dict = self.get_filter_attribute()

        if filter_dict is None:
            return {}

        res = {}
        for key, vals in filter_dict.items():
            try:
                df_filter = df[vals]
                res[key] = DataConverter.id_name_converter(df_filter, vals)

            except KeyError as e:
                print(f"Column '{e.args[0]}' does not exist in the DataFrame")

        return res
