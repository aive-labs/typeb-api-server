from src.audiences.routes.port.usecase.get_audience_usecase import GetAudienceUsecase
from src.audiences.service.port.base_audience_repository import BaseAudienceRepository
from src.common.view_settings import FilterProcessing
from src.users.domain.user import User


class GetAudienceService(GetAudienceUsecase):

    def __init__(self, audience_repository: BaseAudienceRepository):
        self.audience_repository = audience_repository

    def get_all_audiences(self, user: User, is_exclude: bool | None = None):
        audiences, audience_df = self.audience_repository.get_audience(user, is_exclude)

        res = {}

        filter_obj = FilterProcessing("target_audience")
        filters = filter_obj.filter_converter(df=audience_df)

        res["audiences"] = audiences
        res["filters"] = filters
        return res

    def get_audience_details(self, audience_id: int):
        raise NotImplementedError
