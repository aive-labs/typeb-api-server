from abc import ABC, abstractmethod

from src.common.pagination.pagination_response import PaginationResponse
from src.contents.infra.dto.response.contents_menu_response import ContentsMenuResponse
from src.contents.infra.dto.response.contents_response import ContentsResponse


class GetContentsUseCase(ABC):
    @abstractmethod
    def get_contents(self):
        pass

    @abstractmethod
    def get_subjects(self, style_yn: bool) -> list[ContentsMenuResponse]:
        pass

    @abstractmethod
    def get_with_subject(self, code: str) -> dict:
        pass

    @abstractmethod
    def get_contents_list(
        self, based_on, sort_by, current_page, per_page, query=None
    ) -> PaginationResponse[ContentsResponse]:
        pass
