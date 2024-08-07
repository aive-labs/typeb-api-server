from sqlalchemy.orm import Session

from src.common.infra.entity.recommend_products import RecommendProductsModelEntity
from src.search.routes.dto.id_with_item_response import IdWithItemDescription


class RecommendProductsRepository:
    def search_recommend_products(self, keyword: str, db: Session) -> list[IdWithItemDescription]:
        if keyword:
            keyword = f"%{keyword}%"
            result = (
                db.query(
                    RecommendProductsModelEntity.recsys_model_id.label("id"),
                    RecommendProductsModelEntity.recsys_model_name.label("name"),
                    RecommendProductsModelEntity.description.label("description"),
                )
                .filter(
                    RecommendProductsModelEntity.recsys_model_name.ilike(keyword),
                )
                .all()
            )
        else:
            result = db.query(
                RecommendProductsModelEntity.recsys_model_id.label("id"),
                RecommendProductsModelEntity.recsys_model_name.label("name"),
                RecommendProductsModelEntity.description.label("description"),
            ).all()

        return [
            IdWithItemDescription(id=data.id, name=data.name, description=data.description)
            for data in result
        ]
