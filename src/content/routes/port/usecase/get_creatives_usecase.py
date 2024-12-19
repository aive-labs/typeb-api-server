from abc import ABC, abstractmethod

from sqlalchemy.orm import Session

from src.common.pagination.pagination_response import PaginationResponse
from src.content.domain.creatives import Creatives
from src.content.routes.dto.request.contents_create import StyleObject
from src.content.routes.dto.response.creative_base import CreativeBase


class GetCreativesUseCase(ABC):
    @abstractmethod
    def get_creatives(
        self, db: Session, based_on, sort_by, current_page, per_page, asset_type, query
    ) -> PaginationResponse[CreativeBase]:
        pass

    @abstractmethod
    def get_style_list(self, db: Session) -> list[StyleObject]:
        pass

    @abstractmethod
    def get_creatives_detail(self, creative_id: int, db: Session) -> Creatives:
        pass
