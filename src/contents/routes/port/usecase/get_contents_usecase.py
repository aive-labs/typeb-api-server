from abc import ABC, abstractmethod

from sqlalchemy.orm import Session

from src.common.pagination.pagination_response import PaginationResponse
from src.contents.infra.dto.response.contents_menu_response import ContentsMenuResponse
from src.contents.infra.dto.response.contents_response import ContentsResponse


class GetContentsUseCase(ABC):
    @abstractmethod
    def get_contents(self, contents_id, db: Session) -> ContentsResponse:
        pass

    @abstractmethod
    def get_subjects(self, style_yn: bool, db: Session) -> list[ContentsMenuResponse]:
        pass

    @abstractmethod
    def get_with_subject(self, code: str, db: Session) -> dict:
        pass

    @abstractmethod
    def get_contents_list(
        self, db: Session, based_on, sort_by, current_page, per_page, query=None
    ) -> PaginationResponse[ContentsResponse]:
        pass
