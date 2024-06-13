from src.contents.domain.contents import Contents
from src.contents.domain.contents_menu import ContentsMenu
from src.contents.infra.contents_sqlalchemy_repository import ContentsSqlAlchemy
from src.contents.infra.dto.response.contents_response import ContentsResponse
from src.contents.service.port.base_contents_repository import BaseContentsRepository


class ContentsRepository(BaseContentsRepository):
    def __init__(self, contents_sqlalchemy: ContentsSqlAlchemy):
        self.contents_sqlalchemy = contents_sqlalchemy

    def find_by_id(self, id: int):
        raise NotImplementedError

    def find_all(self):
        raise NotImplementedError

    def add_contents(self, contents: Contents):
        return self.contents_sqlalchemy.add_contents(contents.to_entity())

    def get_subject(self, style_yn) -> list[ContentsMenu]:
        return self.contents_sqlalchemy.get_subject(style_yn)

    def get_menu_map(self, code) -> list[ContentsMenu]:
        return self.contents_sqlalchemy.get_menu_map(code)

    def get_contents_list(self, based_on, sort_by, query) -> list[ContentsResponse]:
        return self.contents_sqlalchemy.get_contents_list(
            based_on, sort_by, query=query
        )

    def get_subject_by_code(self, subject: str) -> ContentsMenu:
        return self.contents_sqlalchemy.get_subject_by_code(subject)
