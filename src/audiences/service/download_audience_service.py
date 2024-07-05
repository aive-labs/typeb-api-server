from pandas import DataFrame
from sqlalchemy.orm import Session

from src.audiences.routes.port.usecase.download_audience_usecase import (
    DownloadAudienceUseCase,
)
from src.audiences.service.port.base_audience_repository import BaseAudienceRepository
from src.common.utils.data_converter import DataConverter


class DownloadAudienceService(DownloadAudienceUseCase):

    def __init__(self, audience_repository: BaseAudienceRepository):
        self.audience_repository = audience_repository

    def exec(self, audience_id: str, db: Session) -> DataFrame:
        audience_data = self.audience_repository.get_audience_cust_with_audience_id(
            audience_id, db
        )
        audience_df = DataConverter.convert_query_to_df(audience_data)
        audience_df.columns = ["member_id"]
        return audience_df
