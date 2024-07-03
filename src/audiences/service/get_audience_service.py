from src.audiences.domain.audience import Audience
from src.audiences.routes.dto.response.audience_stat_info import (
    AudienceStats,
    AudienceStatsInfo,
    AudienceSummary,
)
from src.audiences.routes.dto.response.audiences import (
    AudienceFilter,
    AudienceRes,
    AudienceResponse,
    FilterItem,
)
from src.audiences.routes.port.usecase.get_audience_usecase import GetAudienceUseCase
from src.audiences.service.port.base_audience_repository import BaseAudienceRepository
from src.common.utils.data_converter import DataConverter
from src.common.view_settings import FilterProcessing
from src.users.domain.user import User


def convert_to_audience_res(data_dict):
    # Handling rep_list transformation if necessary

    if data_dict["rep_list"] is not None:
        data_dict["rep_list"] = [FilterItem(**item) for item in data_dict["rep_list"]]

    return AudienceRes(**data_dict)


class GetAudienceService(GetAudienceUseCase):

    def __init__(self, audience_repository: BaseAudienceRepository):
        self.audience_repository = audience_repository

    def get_audience_details(self, audience_id: str) -> Audience:
        return self.audience_repository.get_audience_detail(audience_id)

    def get_all_audiences(
        self, user: User, is_exclude: bool | None = None
    ) -> AudienceResponse:
        audiences, audience_df = self.audience_repository.get_audiences(
            user, is_exclude
        )

        if not audiences:
            return AudienceResponse(audiences=[], filters=None)

        audience_response = [
            convert_to_audience_res(audience) for audience in audiences
        ]

        filter_obj = FilterProcessing("target_audience")
        filters = filter_obj.filter_converter(df=audience_df)

        representative_items = []
        if "rep_list" in filters:
            representative_items = [
                FilterItem(id=item["id"], name=item["name"])
                for item in filters["rep_list"]
            ]

        item_owned_by = []
        if "owned_by_dept_list" in filters:
            item_owned_by = [
                FilterItem(id=item["id"], name=item["name"])
                for item in filters["owned_by_dept_list"]
            ]

        response = AudienceResponse(
            audiences=audience_response,
            filters=AudienceFilter(
                rep_list=representative_items,
                owned_by_dept_list=item_owned_by,
            ),
        )

        return response

    def get_audience_stat_details(self, audience_id: str) -> AudienceStatsInfo:

        res = {}

        audience_filtered = self.audience_repository.get_audience_stats(audience_id)
        audience_rep_list = self.audience_repository.get_audience_products(audience_id)
        audience_count_list = self.audience_repository.get_audience_count(
            audience_id=audience_id
        )
        audience_df = DataConverter.convert_query_to_df(audience_filtered)
        audience_df["description"] = audience_df["description"].fillna("")
        audience_df["description"] = audience_df["description"].apply(
            lambda x: x.split(",")
        )
        audience_base = audience_df.to_dict("records")[0]

        audience_reps = DataConverter.convert_query_to_df(audience_rep_list)

        audience_count = DataConverter.convert_query_to_df(audience_count_list)
        audience_count_dicts = audience_count.to_dict("records")

        ## audience_trend
        keys_to_get = [
            "audience_id",
            "audience_name",
            "description",
        ]
        audience_base_dict = DataConverter.get_values_from_dict(
            audience_base, keys_to_get
        )

        res.update(audience_base_dict)

        # audience_stat
        res["audience_stat"] = {}

        keys_to_get = [
            "audience_count",
            "audience_count_gap",
            "audience_portion",
            "audience_portion_gap",
            "audience_unit_price",
            "audience_unit_price_gap",
        ]
        audience_stat_dict = DataConverter.get_values_from_dict(
            audience_base, keys_to_get
        )

        ## audience_trend
        audience_count_dict = DataConverter.extract_key_value_from_dict(
            audience_count_dicts, key="stnd_month", value="audience_count"
        )
        audience_net_count_dict = DataConverter.extract_key_value_from_dict(
            audience_count_dicts, key="stnd_month", value="net_audience_count"
        )

        audience_trend = {}

        audience_trend["name"] = "타겟 고객 수 추이(월)"

        audience_trend["audience"] = {}
        audience_trend["audience"]["legend"] = "타겟 고객수"
        audience_trend["audience"]["values"] = audience_count_dict

        audience_trend["net_audience"] = {}
        audience_trend["net_audience"]["legend"] = "타겟 고객(제외 반영)"
        audience_trend["net_audience"]["values"] = audience_net_count_dict

        ## excluded_audience_info
        excluded_audience_info = []

        res["audience_stat"].update(audience_stat_dict)
        res["audience_stat"]["audience_trend"] = audience_trend
        res["audience_stat"]["excluded_audience_info"] = excluded_audience_info

        # audience_summary

        res["audience_summary"] = {}
        keys_to_get = [
            "revenue_per_audience",
            "purchase_per_audience",
            "revenue_per_purchase",
            "avg_pur_item_count",
            "retention_rate_3m",
            "response_rate",
            "stat_updated_at",
            "created_at",
            "created_by_name",
            "owned_by_dept_name",
            "owned_by_dept_abb_name",
            "create_type_code",
        ]
        audience_summary_dict = DataConverter.get_values_from_dict(
            audience_base, keys_to_get
        )
        keys_to_get = ["agg_period_start", "agg_period_end"]
        audience_agg_peri_dict = DataConverter.get_values_from_dict(
            audience_base, keys_to_get
        )

        filter_col = ["main_product_id", "main_product_name"]
        audience_reps = audience_reps[filter_col]
        audience_rep_dict = DataConverter.id_name_converter(audience_reps, filter_col)

        res["audience_summary"].update(audience_summary_dict)
        res["audience_summary"]["agg_period"] = audience_agg_peri_dict
        res["audience_summary"]["rep_list"] = audience_rep_dict

        return AudienceStatsInfo(
            audience_id=res["audience_id"],
            audience_name=res["audience_name"],
            description=res["description"],
            audience_stat=AudienceStats(**res["audience_stat"]),
            audience_summary=AudienceSummary(**res["audience_summary"]),
        )
