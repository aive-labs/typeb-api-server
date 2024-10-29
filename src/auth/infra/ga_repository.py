from sqlalchemy.orm import Session

from src.auth.domain.ga_integration import GAIntegration
from src.auth.infra.ga_sqlalchemy_repository import GASqlAlchemyRepository
from src.auth.service.port.base_ga_repository import BaseGARepository


class GARepository(BaseGARepository):

    def __init__(self, ga_sqlalchemy: GASqlAlchemyRepository):
        self.ga_sqlalchemy = ga_sqlalchemy

    def get_by_mall_id(self, mall_id: str, db: Session) -> GAIntegration:
        return self.ga_sqlalchemy.get_by_mall_id(mall_id, db)
