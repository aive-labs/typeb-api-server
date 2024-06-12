from src.contents.domain.contents import Contents
from src.contents.domain.contents_menu import ContentsMenu
from src.contents.infra.contents_sqlalchemy_repository import ContentsSqlAlchemy
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
