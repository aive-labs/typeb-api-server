from pandas import DataFrame

from src.audiences.routes.port.usecase.download_audience_usecase import (
    DownloadAudienceUseCase,
)
from src.audiences.service.port.base_audience_repository import BaseAudienceRepository
from src.utils.data_converter import DataConverter


class DownloadAudienceService(DownloadAudienceUseCase):

    def __init__(self, audience_repository: BaseAudienceRepository):
        self.audience_repository = audience_repository

    def exec(self, audience_id: str) -> DataFrame:
        audience_data = self.audience_repository.get_audience_cust_with_audience_id(
            audience_id
        )
        audience_df = DataConverter.convert_query_to_df(audience_data)
        return audience_df
