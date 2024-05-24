from src.contents.domain.contents import Contents
from src.contents.infra.contents_sqlalchemy_repository import ContentsSqlAlchemy
from src.contents.service.port.base_contents_repository import BaseContentsRepository


class ContentsRepository(BaseContentsRepository):

    def __init__(self, content_sqlalchemy: ContentsSqlAlchemy):
        self.content_sqlalchemy: ContentsSqlAlchemy

    def find_by_id(self, id: int):
        raise NotImplementedError

    def find_all(self):
        raise NotImplementedError

    def add_contents(self, contents: Contents):
        return self.content_sqlalchemy.add_contents(contents.to_entity())
