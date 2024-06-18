from typing import Any

from pandas import DataFrame
from sqlalchemy.orm.query import Query

from src.audiences.domain.audience import Audience
from src.audiences.domain.variable_table_mapping import VariableTableMapping
from src.audiences.infra.audience_sqlalchemy_repository import AudienceSqlAlchemy
from src.audiences.infra.dto.linked_campaign import LinkedCampaign
from src.audiences.service.port.base_audience_repository import BaseAudienceRepository
from src.users.domain.user import User
from src.utils.data_converter import DataConverter


class AudienceRepository(BaseAudienceRepository):
    def __init__(self, audience_sqlalchemy: AudienceSqlAlchemy):
        self.audience_sqlalchemy = audience_sqlalchemy

    def get_audiences(
        self, user: User, is_exclude: bool | None = None
    ) -> tuple[list[dict[Any, Any]], DataFrame]:
        audiences_info = self.audience_sqlalchemy.get_audiences(
            user=user, is_exclude=is_exclude
        )

        print(audiences_info)

        audience_df = DataConverter.pydantic_to_df(audiences_info)

        audience_base = (
            audience_df.drop(columns=["main_product_id", "main_product_name"])
            .drop_duplicates()
            .to_dict("records")
        )

        audience_reps = audience_df[
            ["audience_id", "main_product_id", "main_product_name"]
        ]

        audience_reps_dict = audience_reps.to_dict(
            "records"  # pyright: ignore [reportArgumentType]
        )

        added_dict = DataConverter.iditems_group_conv_by_key(
            audience_reps_dict,  # pyright: ignore [reportArgumentType]
            key_field="audience_id",
            items_group_name="rep_list",
            code_field="main_product_id",
            name_field="main_product_name",
        )

        merged_data = DataConverter.merge_dict_by_key(
            audience_base, added_dict, key_field="audience_id"
        )

        return merged_data, audience_df

    def get_audience_stats(self, audience_id: str) -> object:
        return self.audience_sqlalchemy.get_audience_stats(audience_id)

    def get_audience_products(self, audience_id: str) -> object:
        return self.audience_sqlalchemy.get_audience_products(audience_id)

    def get_audience_count(self, audience_id: str) -> object:
        return self.audience_sqlalchemy.get_audience_count(audience_id)

    def get_audience(self, audience_id: str) -> Audience:
        audience_entity = self.audience_sqlalchemy.get_audience(audience_id=audience_id)
        audience = Audience.from_entity(audience_entity)
        return audience

    def get_linked_campaigns(self, audience_id: str) -> list[LinkedCampaign]:
        return self.audience_sqlalchemy.get_linked_campaign(audience_id)

    def update_expired_audience_status(self, audience_id: str) -> None:
        self.audience_sqlalchemy.update_expired_audience_status(audience_id)

    def delete_audience(self, audience_id: str):
        return self.audience_sqlalchemy.delete_audience(audience_id)

    def get_audience_by_name(self, audience_name: str) -> Audience | None:
        audience_entity = self.audience_sqlalchemy.get_audience_by_name(audience_name)

        if audience_entity is not None:
            audience = Audience.from_entity(audience_entity)
            return audience
        else:
            return None

    def create_audience(self, audience_dict, conditions) -> str:
        audience_id = self.audience_sqlalchemy.create_audience(
            audience_dict, conditions
        )
        return audience_id

    def create_audience_by_upload(
        self, audience_dict, insert_to_uploaded_audiences, upload_check_list
    ) -> str:
        audience_id = self.audience_sqlalchemy.create_audience_by_upload(
            audience_dict, insert_to_uploaded_audiences, upload_check_list
        )
        return audience_id

    def get_db_filter_conditions(self, audience_id: str):
        return self.audience_sqlalchemy.get_db_filter_conditions(audience_id)

    def save_audience_list(self, audience_id, query):
        self.audience_sqlalchemy.save_audience_list(audience_id, query)

    def get_all_customer_by_audience(self, user: User) -> Query[Any]:
        if user.erp_id is not None and user.sys_id is not None:
            return self.audience_sqlalchemy.get_all_customer(user.erp_id, user.sys_id)
        else:
            raise Exception("erp_id와 sys_id가 존재하지 않습니다.")

    def get_tablename_by_variable_id(self, variable_id: str) -> VariableTableMapping:
        return self.audience_sqlalchemy.get_tablename_by_variable_id(variable_id)

    def get_subquery_with_select_query_list(self, table_obj, select_query_list, idx):
        return self.audience_sqlalchemy.get_subquery_with_select_query_list(
            table_obj, select_query_list, idx
        )

    def get_subquery_with_array_select_query_list(
        self, table_obj, array_select_query_list, idx
    ):
        return self.audience_sqlalchemy.get_subquery_with_array_select_query_list(
            table_obj, array_select_query_list, idx
        )

    def get_variable_options(self, access_lv):
        return self.audience_sqlalchemy.get_variables_options(access_lv)

    def get_options(self):
        return self.audience_sqlalchemy.get_options()
