from abc import ABC, abstractmethod

from sqlalchemy.orm import Session

from src.contents.domain.contents import Contents
from src.contents.domain.contents_menu import ContentsMenu
from src.contents.infra.dto.response.contents_response import ContentsResponse
from src.search.routes.dto.id_with_item_response import IdWithItem


class BaseContentsRepository(ABC):

    @abstractmethod
    def add_contents(self, contents: Contents, db: Session) -> ContentsResponse:
        pass

    @abstractmethod
    def get_subject(self, style_yn, db: Session) -> list[ContentsMenu]:
        pass

    @abstractmethod
    def get_menu_map(self, code, db: Session) -> list[ContentsMenu]:
        pass

    @abstractmethod
    def get_contents_list(self, db: Session, based_on, sort_by, query) -> list[ContentsResponse]:
        pass

    @abstractmethod
    def get_subject_by_code(self, subject: str, db: Session) -> ContentsMenu:
        pass

    @abstractmethod
    def get_contents_url_list(self, db: Session) -> list[str]:
        pass

    @abstractmethod
    def get_contents_detail(self, contents_id: int, db: Session) -> ContentsResponse:
        pass

    @abstractmethod
    def delete(self, contents_id: int, db: Session):
        pass

    @abstractmethod
    def update(self, contents_id: int, contents: Contents, db: Session) -> ContentsResponse:
        pass

    @abstractmethod
    def search_contents_tag(self, keyword, recsys_model_id, db: Session) -> list[IdWithItem]:
        pass

    @abstractmethod
    def count_contents_by_campaign_id(self, campaign_id, set_group_seqs, db: Session) -> int:
        pass

    @abstractmethod
    def get_contents_by_tags(self, contents_tags, db: Session, keyword=None) -> list[IdWithItem]:
        pass

    @abstractmethod
    def get_contents_id_url_dict(self, db: Session) -> dict:
        pass
