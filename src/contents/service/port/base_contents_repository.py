from abc import ABC, abstractmethod

from src.contents.domain.contents import Contents


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
