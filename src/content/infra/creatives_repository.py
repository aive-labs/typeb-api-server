from sqlalchemy.orm import Session

from src.content.domain.creatives import Creatives
from src.content.infra.creatives_sqlalchemy_repository import CreativesSqlAlchemy
from src.content.infra.dto.response.creative_recommend import CreativeRecommend
from src.content.routes.dto.response.creative_base import CreativeBase
from src.content.service.port.base_creatives_repository import BaseCreativesRepository


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

    def get_creatives_by_style_cd(self, style_cd: str, db: Session) -> list[CreativeBase]:
        return self.creative_sqlalchemy.get_creatives_by_style_cd(style_cd, db)

    def get_creatives_by_id(self, creative_id, db) -> Creatives:
        return self.creative_sqlalchemy.get_creative_by_id(creative_id, db)
