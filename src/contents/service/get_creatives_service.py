from src.common.pagination.pagination_base import PaginationBase
from src.common.pagination.pagination_response import PaginationResponse
from src.contents.routes.dto.response.creative_base import CreativeBase
from src.contents.routes.port.usecase.get_creatives_usecase import GetCreativesUseCase
from src.contents.service.port.base_creatives_repository import BaseCreativesRepository
from src.users.service.port.base_user_repository import BaseUserRepository


class GetCreativesService(GetCreativesUseCase):
    def __init__(
        self,
        creatives_repository: BaseCreativesRepository,
        user_repository: BaseUserRepository,
    ):
        self.creatives_repository = creatives_repository
        self.user_repository = user_repository

    def get_creatives(
        self, based_on, sort_by, current_page, per_page, asset_type=None, query=None
    ) -> PaginationResponse[CreativeBase]:
        creative_data = self.creatives_repository.find_all(
            based_on, sort_by, asset_type, query
        )
        items = [CreativeBase.model_validate(item) for item in creative_data]

        pagination = PaginationBase(
            total=len(items),
            per_page=per_page,
            current_page=current_page,
            total_page=len(creative_data) // per_page + 1,
        )

        return PaginationResponse[CreativeBase](
            status="success", items=items, pagination=pagination
        )
