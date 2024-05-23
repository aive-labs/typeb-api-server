from src.contents.infra.creatives_sqlalchemy_repository import CreativesSqlAlchemy
from src.contents.service.port.base_creatives_repository import BaseCreativesRepository


class CreativesRepository(BaseCreativesRepository):

    def __init__(self, creative_sqlalchemy: CreativesSqlAlchemy):
        self.creative_sqlalchemy = creative_sqlalchemy

    def find_by_id(self, id: int):
        raise NotImplementedError

    def find_all(self, based_on, sort_by, asset_type=None, query=None):
        creatives = self.creative_sqlalchemy.get_all_creatives(
            based_on=based_on, sort_by=sort_by, asset_type=asset_type, query=query
        )
        return creatives
