from copy import deepcopy
from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class GAIntegration(BaseModel):
    mall_id: str
    ga_account_id: int
    ga_account_name: str
    ga_property_id: int | None = None
    ga_property_name: str | None = None
    ga_measurement_id: str | None = None
    ga_data_stream_id: int | None = None
    ga_data_stream_uri: str | None = None
    ga_data_stream_name: str | None = None
    ga_data_stream_type: str | None = None
    gtm_account_id: int
    gtm_account_name: str
    gtm_container_id: int | None = None
    gtm_container_name: str | None = None
    gtm_tag_id: str | None = None
    ga_script: str | None = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

    @staticmethod
    def init(mall_id, ga_account_id, ga_account_name, gtm_account_id, gtm_account_name):
        return GAIntegration(
            mall_id=mall_id,
            ga_account_id=ga_account_id,
            ga_account_name=ga_account_name,
            gtm_account_id=gtm_account_id,
            gtm_account_name=gtm_account_name,
        )

    def set_ga_property(self, property_id: int, property_name: str) -> "GAIntegration":
        # Create a copy of the current instance
        new_instance = deepcopy(self)

        # Set new property id and name
        new_instance.ga_property_id = property_id
        new_instance.ga_property_name = property_name

        return new_instance

    def set_ga_data_stream(
        self, measurement_id, data_stream_id, data_stream_name, data_stream_url, data_stream_type
    ) -> "GAIntegration":
        # Create a copy of the current instance
        new_instance = deepcopy(self)

        # Set new property id and name
        new_instance.measurement_id = measurement_id
        new_instance.data_stream_id = data_stream_id
        new_instance.data_stream_name = data_stream_name
        new_instance.data_stream_url = data_stream_url
        new_instance.data_stream_type = data_stream_type

        return new_instance

    def set_gtm_container(
        self, container_id: int, container_name: str, gtm_tag_id: str
    ) -> "GAIntegration":
        # Create a copy of the current instance
        new_instance = deepcopy(self)

        # Set new property id and name
        new_instance.gtm_container_id = container_id
        new_instance.gtm_container_name = container_name
        new_instance.gtm_tag_id = gtm_tag_id

        return new_instance
