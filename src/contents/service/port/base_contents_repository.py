from abc import ABC, abstractmethod

from src.contents.domain.contents import Contents
from src.contents.domain.contents_menu import ContentsMenu
from src.contents.infra.dto.response.contents_response import ContentsResponse


class BaseContentsRepository(ABC):
    @abstractmethod
    def find_by_id(self, id: int):
        pass

    @abstractmethod
    def find_all(self):
        pass

    @abstractmethod
    def add_contents(self, contents: Contents) -> Contents:
        pass

    @abstractmethod
    def get_subject(self, style_yn) -> list[ContentsMenu]:
        pass

    @abstractmethod
    def get_menu_map(self, code) -> list[ContentsMenu]:
        pass

    @abstractmethod
    def get_contents_list(self, based_on, sort_by, query) -> list[ContentsResponse]:
        pass

    @abstractmethod
    def get_subject_by_code(self, subject: str) -> ContentsMenu:
        pass

    @abstractmethod
    def get_contents_url_list(self) -> list[str]:
        pass

    @abstractmethod
    def get_contents_detail(self, contents_id: int) -> Contents:
        pass

    @abstractmethod
    def delete(self, contents_id: int):
        pass

    @abstractmethod
    def update(self, contents_id: int, contents: Contents):
        pass
