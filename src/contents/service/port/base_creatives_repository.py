from abc import ABC, abstractmethod

from sqlalchemy.orm import Session

from src.contents.domain.creatives import Creatives
from src.contents.infra.dto.response.creative_recommend import CreativeRecommend
from src.contents.routes.dto.response.creative_base import CreativeBase


class BaseCreativesRepository(ABC):
    @abstractmethod
    def find_by_id(self, id: int, db: Session) -> Creatives:
        pass

    @abstractmethod
    def find_all(
        self, based_on, sort_by, db: Session, asset_type=None, query=None
    ) -> list[CreativeBase]:
        pass

    @abstractmethod
    def get_simple_style_list(self, db: Session) -> list:
        pass

    @abstractmethod
    def update_creatives(
        self, creative_id, creative_update_dict: dict, db: Session
    ) -> Creatives:
        pass

    @abstractmethod
    def create_creatives(self, creatives_list, db: Session):
        pass

    @abstractmethod
    def delete(self, creative_id, db: Session):
        pass

    @abstractmethod
    def get_creatives_for_contents(
        self, style_cd_list, given_tag, tag_nm, limit, db: Session
    ) -> list[CreativeRecommend]:
        pass
