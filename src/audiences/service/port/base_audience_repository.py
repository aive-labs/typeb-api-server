from abc import ABC, abstractmethod
from typing import Any

from pandas import DataFrame

from src.audiences.domain.audience import Audience
from src.audiences.domain.variable_table_mapping import VariableTableMapping
from src.audiences.infra.dto.filter_condition import FilterCondition
from src.audiences.infra.dto.linked_campaign import LinkedCampaign
from src.audiences.infra.dto.upload_conditon import UploadCondition
from src.users.domain.user import User


class BaseAudienceRepository(ABC):

    @abstractmethod
    def get_audience_detail(self, audience_id: str) -> Audience:
        pass

    @abstractmethod
    def get_audiences(
        self, user: User, is_exclude: bool | None = None
    ) -> tuple[list[dict[Any, Any]], DataFrame]:
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
    def get_subquery_with_select_query_list(self, table_obj, select_query_list, idx):
        pass

    @abstractmethod
    def get_subquery_with_array_select_query_list(
        self, table_obj, array_select_query_list, idx
    ):
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
