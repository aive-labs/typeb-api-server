from contextlib import AbstractContextManager
from typing import Callable

from sqlalchemy.orm import Session

from src.common.infra.entity.recommend_products import RecommendProductsModelEntity
from src.search.routes.dto.id_with_item_response import IdWithItemDescription


class RecommendProductsRepository:
    def __init__(self, db: Callable[..., AbstractContextManager[Session]]):
        """_summary_

        Args:
            db (Callable[..., AbstractContextManager[Session]]):
            - Callable 호출 가능한 객체
            - AbstractContextManager[Session]: 세션 객체를 반환하는 컨텍스트 관리자
            - Session: SQLAlchemy의 세션 객체

        """
        self.db = db

    def search_recommend_products(self, keyword: str) -> list[IdWithItemDescription]:
        with self.db() as db:
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
