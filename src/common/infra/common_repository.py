from sqlalchemy.orm import Session

from src.common.domain.recsys_models import RecsysModels
from src.common.infra.entity.recommend_products import RecommendProductsModelEntity
from src.common.service.port.base_common_repository import BaseCommonRepository


class CommonRepository(BaseCommonRepository):
    def get_recsys_model(self, recsys_model_id: int, db: Session) -> RecsysModels:
        result = (
            db.query(RecommendProductsModelEntity)
            .filter(RecommendProductsModelEntity.recsys_model_id == recsys_model_id)
            .first()
        )

        return result
