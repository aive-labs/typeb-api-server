from src.contents.domain.creatives import Creatives
from src.contents.infra.creatives_sqlalchemy_repository import CreativesSqlAlchemy
from src.contents.routes.dto.request.creatives_create import CreativeCreate
from src.contents.routes.dto.response.creative_base import CreativeBase
from src.contents.service.port.base_creatives_repository import BaseCreativesRepository


class CreativesRepository(BaseCreativesRepository):

    def __init__(self, creative_sqlalchemy: CreativesSqlAlchemy):
        self.creative_sqlalchemy = creative_sqlalchemy

    def find_by_id(self, id: int) -> Creatives:
        return self.creative_sqlalchemy.find_by_id(id)

    def find_all(
        self, based_on, sort_by, asset_type=None, query=None
    ) -> list[CreativeBase]:
        creatives = self.creative_sqlalchemy.get_all_creatives(
            based_on=based_on, sort_by=sort_by, asset_type=asset_type, query=query
        )
        return creatives

    def get_simple_style_list(self):
        return self.creative_sqlalchemy.get_simple_style_list()

    def update_creatives(
        self, creative_id: str, creative_update: CreativeCreate, pre_fix: str
    ):
        return self.creative_sqlalchemy.update(creative_id, creative_update, pre_fix)

    def create_creatives(self, creatives_list):
        return self.creative_sqlalchemy.save_creatives(creatives_list)
