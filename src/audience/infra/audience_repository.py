from typing import Any

from pandas import DataFrame
from sqlalchemy.orm import Session
from sqlalchemy.sql import Alias

from src.audience.domain.audience import Audience
from src.audience.domain.variable_table_mapping import VariableTableMapping
from src.audience.infra.audience_sqlalchemy_repository import AudienceSqlAlchemy
from src.audience.model.filter_condition import FilterCondition
from src.audience.model.linked_campaign import LinkedCampaign
from src.audience.model.response.default_exclude_audience import (
    DefaultExcludeAudience,
)
from src.audience.model.upload_conditon import UploadCondition
from src.audience.service.port.base_audience_repository import BaseAudienceRepository
from src.common.utils.data_converter import DataConverter
from src.search.model.id_with_label_response import IdWithLabel
from src.user.domain.user import User


class AudienceRepository(BaseAudienceRepository):

    def __init__(self, audience_sqlalchemy: AudienceSqlAlchemy):
        self.audience_sqlalchemy = audience_sqlalchemy

    def get_audience_detail(self, audience_id: str, db: Session) -> Audience:
        return self.audience_sqlalchemy.get_audience_detail(audience_id, db)

    def get_audiences(
        self, user: User, db: Session, is_exclude: bool | None = None
    ) -> tuple[list[dict[Any, Any]] | None, DataFrame | None]:
        audiences_info = self.audience_sqlalchemy.get_audiences(
            user=user, db=db, is_exclude=is_exclude
        )

        if not audiences_info:
            return (None, None)

        audience_df = DataConverter.pydantic_to_df(audiences_info)

        audience_base = (
            audience_df.drop(columns=["main_product_id", "main_product_name"])
            .drop_duplicates()
            .to_dict("records")
        )

        audience_reps = audience_df[["audience_id", "main_product_id", "main_product_name"]]

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

    def get_audience_stats(self, audience_id: str, db: Session) -> object:
        return self.audience_sqlalchemy.get_audience_stats(audience_id, db)

    def get_audience_products(self, audience_id: str, db: Session) -> object:
        return self.audience_sqlalchemy.get_audience_products(audience_id, db)

    def get_audience_count(self, audience_id: str, db: Session) -> object:
        return self.audience_sqlalchemy.get_audience_count(audience_id, db)

    def get_audience(self, audience_id: str, db: Session) -> Audience:
        audience_entity = self.audience_sqlalchemy.get_audience(audience_id, db)
        audience = Audience.from_entity(audience_entity)
        return audience

    def get_linked_campaigns(self, audience_id: str, db: Session) -> list[LinkedCampaign]:
        return self.audience_sqlalchemy.get_linked_campaign(audience_id, db)

    def update_expired_audience_status(self, audience_id: str, db: Session) -> None:
        self.audience_sqlalchemy.update_expired_audience_status(audience_id, db)

    def delete_audience(self, audience_id: str, db: Session):
        return self.audience_sqlalchemy.delete_audience(audience_id, db)

    def get_audience_by_name(self, audience_name: str, db: Session) -> Audience | None:
        audience_entity = self.audience_sqlalchemy.get_audience_by_name(audience_name, db)

        if audience_entity is not None:
            audience = Audience.from_entity(audience_entity)
            return audience
        else:
            return None

    def create_audience(self, audience_dict, conditions, db: Session) -> str:
        audience_id = self.audience_sqlalchemy.create_audience(audience_dict, conditions, db)
        return audience_id

    def create_audience_by_upload(
        self,
        audience_dict,
        insert_to_uploaded_audiences,
        upload_check_list,
        db: Session,
    ) -> str:
        audience_id = self.audience_sqlalchemy.create_audience_by_upload(
            audience_dict, insert_to_uploaded_audiences, upload_check_list, db
        )
        return audience_id

    def get_db_filter_conditions(self, audience_id: str, db: Session) -> list[FilterCondition]:
        return self.audience_sqlalchemy.get_db_filter_conditions(audience_id, db)

    def save_audience_list(self, audience_id, query, db: Session):
        self.audience_sqlalchemy.save_audience_list(audience_id, query, db)

    def get_all_customer_by_audience(self, user: User, db: Session) -> object:
        return self.audience_sqlalchemy.get_all_customer(db)

    def get_tablename_by_variable_id(self, variable_id: str, db: Session) -> VariableTableMapping:
        return self.audience_sqlalchemy.get_tablename_by_variable_id(variable_id, db)

    def get_subquery_with_select_query_list(
        self, table_obj, select_query_list, idx, db: Session
    ) -> Alias:
        return self.audience_sqlalchemy.get_subquery_with_select_query_list(
            table_obj, select_query_list, idx, db
        )

    def get_subquery_with_array_select_query_list(
        self, table_obj, array_select_query_list, idx, db: Session
    ) -> Alias:
        return self.audience_sqlalchemy.get_subquery_with_array_select_query_list(
            table_obj, array_select_query_list, idx, db
        )

    def get_variable_options(self, access_lv, db: Session):
        return self.audience_sqlalchemy.get_variables_options(access_lv, db)

    def get_options(self, db: Session):
        return self.audience_sqlalchemy.get_options(db)

    def get_audience_cust_with_audience_id(self, audience_id: str, db: Session) -> object:
        return self.audience_sqlalchemy.get_audience_cust_with_audience_id(audience_id, db)

    def get_audience_upload_info(self, audience_id: str, db: Session) -> list[UploadCondition]:
        return self.audience_sqlalchemy.get_audience_upload_info(audience_id, db)

    def get_actual_list_from_csv(self, uploaded_rows, target_column, entity, db: Session) -> list:
        return self.audience_sqlalchemy.get_actual_list_from_csv(
            uploaded_rows, target_column, entity, db
        )

    def update_cycle(self, audience_id, update_cycle, db: Session):
        self.audience_sqlalchemy.update_cycle(audience_id, update_cycle, db)

    def delete_audience_info_for_update(self, audience_id, db: Session):
        self.audience_sqlalchemy.delete_audience_info_for_update(audience_id, db)

    def update_by_filter(
        self, audience_id, insert_to_filter_conditions, insert_to_audiences, db: Session
    ):
        self.audience_sqlalchemy.update_by_filter(
            audience_id, insert_to_filter_conditions, insert_to_audiences, db
        )

    def update_by_upload(
        self,
        filter_audience,
        insert_to_uploaded_audiences,
        insert_to_audiences,
        checked_list,
        db: Session,
    ):
        self.audience_sqlalchemy.update_by_upload(
            filter_audience,
            insert_to_uploaded_audiences,
            insert_to_audiences,
            checked_list,
            db,
        )

    def get_audiences_ids_by_strategy_id(
        self, strategy_id: str, db: Session, strategy_theme_id: str | None = None
    ) -> list[str]:
        return self.audience_sqlalchemy.get_audiences_ids_by_strategy_id(
            strategy_id, db, strategy_theme_id
        )

    def get_audiences_by_condition(
        self,
        audience_ids: list[str],
        search_keyword: str,
        is_exclude: bool,
        db: Session,
    ) -> list[IdWithLabel]:
        return self.audience_sqlalchemy.get_audiences_by_condition(
            audience_ids, search_keyword, is_exclude, db
        )

    def get_audiences_by_condition_without_strategy_id(
        self,
        search_keyword,
        is_exclude,
        db: Session,
        target_strategy: str | None = None,
    ) -> list[IdWithLabel]:
        return self.audience_sqlalchemy.get_audiences_by_condition_without_strategy_id(
            search_keyword, is_exclude, db, target_strategy
        )

    def get_default_exclude(self, user: User, db: Session) -> list[DefaultExcludeAudience]:
        return self.audience_sqlalchemy.get_default_exclude(user, db)

    def update_exclude_status(self, audience_id: str, is_exclude: bool, db: Session):
        self.audience_sqlalchemy.update_exclude_status(audience_id, is_exclude, db)

    def get_linked_strategy(self, audience_id: str, db: Session) -> list:
        return self.audience_sqlalchemy.get_linked_strategy(audience_id, db)
