from src.audiences.service.port.base_audience_repository import BaseAudienceRepository
from src.search.routes.dto.id_with_label_response import IdWithLabel
from src.search.routes.port.base_search_service import BaseSearchService
from src.users.domain.user import User


class SearchService(BaseSearchService):

    def __init__(self, audience_repository: BaseAudienceRepository):
        self.audience_repository = audience_repository

    def search_audience_with_strategy_id(
        self, strategy_id: str, search_keyword: str, user: User, is_exclude=False
    ) -> list[IdWithLabel]:
        audience_ids = self.audience_repository.get_audiences_ids_by_strategy_id(
            strategy_id
        )
        return self.audience_repository.get_audiences_by_condition(
            audience_ids, search_keyword, is_exclude
        )

    def search_audience_without_strategy_id(
        self, audience_type_code: str, search_keyword, is_exclude=False
    ) -> list[IdWithLabel]:
        return self.audience_repository.get_audiences_by_condition_without_strategy_id(
            audience_type_code, search_keyword, is_exclude
        )
