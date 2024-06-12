from abc import ABC, abstractmethod

from src.contents.infra.dto.response.contents_menu_response import ContentsMenuResponse


class GetContentsUseCase(ABC):
    @abstractmethod
    def get_contents(self):
        pass

    @abstractmethod
    def get_subjects(self, style_yn: bool) -> list[ContentsMenuResponse]:
        pass

    @abstractmethod
    def get_with_subject(self, code: str):
        pass
