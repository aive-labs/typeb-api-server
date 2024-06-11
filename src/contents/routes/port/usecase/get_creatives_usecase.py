from abc import ABC, abstractmethod

from src.common.pagination.pagination_response import PaginationResponse
from src.contents.domain.creatives import Creatives
from src.contents.routes.dto.request.contents_create import StyleObjectBase
from src.contents.routes.dto.response.creative_base import CreativeBase


class GetCreativesUseCase(ABC):
    @abstractmethod
    def get_creatives(
        self, based_on, sort_by, current_page, per_page, asset_type, query
    ) -> PaginationResponse[CreativeBase]:
        pass

    @abstractmethod
    def get_style_list(self) -> list[StyleObjectBase]:
        pass

    @abstractmethod
    def get_creatives_detail(self, creative_id: int) -> Creatives:
        pass
