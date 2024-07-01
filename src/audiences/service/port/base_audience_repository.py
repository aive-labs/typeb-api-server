from abc import ABC, abstractmethod
from typing import Any

from pandas import DataFrame
from sqlalchemy.sql import Alias

from src.audiences.domain.audience import Audience
from src.audiences.domain.variable_table_mapping import VariableTableMapping
from src.audiences.infra.dto.filter_condition import FilterCondition
from src.audiences.infra.dto.linked_campaign import LinkedCampaign
from src.audiences.infra.dto.upload_conditon import UploadCondition
from src.search.routes.dto.id_with_label_response import IdWithLabel
from src.users.domain.user import User


class BaseAudienceRepository(ABC):

    @abstractmethod
    def get_audience_detail(self, audience_id: str) -> Audience:
        pass

    @abstractmethod
    def get_audiences(
        self, user: User, is_exclude: bool | None = None
    ) -> tuple[list[dict[Any, Any]] | None, DataFrame | None]:
        pass

    @abstractmethod
    def get_audience_stats(self, audience_id: str) -> object:
        pass

    @abstractmethod
    def get_audience_products(self, audience_id: str) -> object:
        pass

    @abstractmethod
    def get_audience_count(self, audience_id: str) -> object:
        pass

    @abstractmethod
    def get_audience(self, audience_id: str) -> Audience:
        pass

    @abstractmethod
    def get_audience_by_name(self, audience_name: str) -> Audience | None:
        pass

    @abstractmethod
    def get_linked_campaigns(self, audience_id: str) -> list[LinkedCampaign]:
        pass

    @abstractmethod
    def update_expired_audience_status(self, audience_id: str):
        pass

    @abstractmethod
    def delete_audience(self, audience_id: str):
        pass

    @abstractmethod
    def create_audience(self, audience_dict, conditions) -> str:
        pass

    @abstractmethod
    def create_audience_by_upload(
        self, audience_dict, insert_to_uploaded_audiences, upload_check_list
    ) -> str:
        pass

    @abstractmethod
    def get_db_filter_conditions(self, audience_id: str) -> list[FilterCondition]:
        pass

    @abstractmethod
    def save_audience_list(self, audience_id, query):
        pass

    @abstractmethod
    def get_all_customer_by_audience(self, user: User) -> object:
        pass

    @abstractmethod
    def get_tablename_by_variable_id(self, variable_id: str) -> VariableTableMapping:
        pass

    @abstractmethod
    def get_subquery_with_select_query_list(
        self, table_obj, select_query_list, idx
    ) -> Alias:
        pass

    @abstractmethod
    def get_subquery_with_array_select_query_list(
        self, table_obj, array_select_query_list, idx
    ) -> Alias:
        pass

    @abstractmethod
    def get_audience_cust_with_audience_id(self, audience_id: str) -> object:
        pass

    @abstractmethod
    def get_audience_upload_info(self, audience_id: str) -> list[UploadCondition]:
        pass

    @abstractmethod
    def get_actual_list_from_csv(self, uploaded_rows, target_column, entity) -> list:
        pass

    @abstractmethod
    def update_cycle(self, audience_id, update_cycle):
        pass

    @abstractmethod
    def delete_audience_info_for_update(self, audience_id):
        pass

    @abstractmethod
    def update_by_filter(
        self, audience_id, insert_to_filter_conditions, insert_to_audiences
    ):
        pass

    @abstractmethod
    def update_by_upload(
        self,
        filter_audience,
        insert_to_uploaded_audiences,
        insert_to_audiences,
        checked_list,
    ):
        pass

    @abstractmethod
    def get_audiences_ids_by_strategy_id(self, strategy_id: str) -> list[str]:
        pass

    @abstractmethod
    def get_audiences_by_condition(
        self, audience_ids: list[str], search_keyword: str, is_exclude: bool
    ) -> list[IdWithLabel]:
        pass

    @abstractmethod
    def get_audiences_by_condition_without_strategy_id(
        self, search_keyword, is_exclude, target_strategy: str | None = None
    ) -> list[IdWithLabel]:
        pass
