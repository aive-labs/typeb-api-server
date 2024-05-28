from typing import Any

from pandas import DataFrame

from src.audiences.domain.audience import Audience
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

        audience_df = DataConverter.pydantic_to_df(audiences_info)

        audience_base = (
            audience_df.drop(columns=["main_product_id", "main_product_name"])
            .drop_duplicates()
            .to_dict("records")
        )

        audience_reps = audience_df[
            ["audience_id", "main_product_id", "main_product_name"]
        ]

        audience_reps_dict = audience_reps.to_dict("records")

        added_dict = DataConverter.iditems_group_conv_by_key(
            audience_reps_dict,
            key_field="audience_id",
            items_group_name="rep_list",
            code_field="main_product_id",
            name_field="main_product_name",
        )

        merged_data = DataConverter.merge_dict_by_key(
            audience_base, added_dict, key_field="audience_id"
        )

        return merged_data, audience_df

    def get_audience_stats(self, audience_id: str):
        raise NotImplementedError

    def get_audience_products(self, audience_id: str):
        raise NotImplementedError

    def get_audience_count(self, audience_id: str):
        raise NotImplementedError

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
