from sqlalchemy.orm import Session

from src.contents.domain.creatives import Creatives
from src.contents.infra.creatives_sqlalchemy_repository import CreativesSqlAlchemy
from src.contents.infra.dto.response.creative_recommend import CreativeRecommend
from src.contents.routes.dto.response.creative_base import CreativeBase
from src.contents.service.port.base_creatives_repository import BaseCreativesRepository


class CreativesRepository(BaseCreativesRepository):

    def __init__(self, creative_sqlalchemy: CreativesSqlAlchemy):
        self.creative_sqlalchemy = creative_sqlalchemy

    def find_by_id(self, id: int, db: Session) -> Creatives:
        return self.creative_sqlalchemy.find_by_id(id, db)

    def find_all(
        self, based_on, sort_by, db: Session, asset_type=None, query=None
    ) -> list[CreativeBase]:
        creatives = self.creative_sqlalchemy.get_all_creatives(
            based_on=based_on,
            sort_by=sort_by,
            db=db,
            asset_type=asset_type,
            query=query,
        )
        return creatives

    def get_simple_style_list(self, db: Session):
        return self.creative_sqlalchemy.get_simple_style_list(db)

    def update_creatives(
        self, creative_id: int, creative_update_dict: dict, db: Session
    ) -> Creatives:
        return self.creative_sqlalchemy.update(creative_id, creative_update_dict, db)

    def create_creatives(self, creatives_list, db: Session):
        return self.creative_sqlalchemy.save_creatives(creatives_list, db)

    def delete(self, creative_id, db: Session):
        self.creative_sqlalchemy.delete(creative_id, db)

    def get_creatives_for_contents(
        self, style_cd_list, given_tag, tag_nm, limit, db: Session
    ) -> list[CreativeRecommend]:
        return self.creative_sqlalchemy.get_creatives_for_contents(
            style_cd_list, given_tag, tag_nm, limit, db
        )
