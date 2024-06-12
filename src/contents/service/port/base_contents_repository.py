from abc import ABC, abstractmethod

from src.contents.domain.contents import Contents
from src.contents.domain.contents_menu import ContentsMenu


class BaseContentsRepository(ABC):
    @abstractmethod
    def find_by_id(self, id: int):
        pass

    @abstractmethod
    def find_all(self):
        pass

    @abstractmethod
    def add_contents(self, contents: Contents):
        pass

    @abstractmethod
    def get_subject(self, style_yn) -> list[ContentsMenu]:
        pass
