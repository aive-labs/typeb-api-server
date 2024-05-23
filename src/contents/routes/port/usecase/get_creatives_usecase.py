from abc import ABC, abstractmethod

from src.common.pagination.pagination_response import PaginationResponse
from src.contents.routes.dto.response.creative_base import CreativeBase


class GetCreativesUseCase(ABC):

    @abstractmethod
    def get_creatives(
        self, based_on, sort_by, current_page, per_page, asset_type, query
    ) -> PaginationResponse[CreativeBase]:
        pass
