from contextlib import AbstractContextManager
from typing import Callable

from sqlalchemy.orm import Session

from src.common.infra.entity.recommend_products import RecommendProductsModel
from src.search.routes.dto.id_with_item_response import IdWithItem


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

    def search_recommend_products(
        self, audience_type_code: str, keyword: str
    ) -> list[IdWithItem]:
        with self.db() as db:
            if keyword:
                keyword = f"%{keyword}%"
                result = (
                    db.query(
                        RecommendProductsModel.recsys_model_id.label("id"),
                        RecommendProductsModel.recsys_model_name.label("name"),
                    )
                    .filter(
                        RecommendProductsModel.recsys_model_name.ilike(keyword),
                        RecommendProductsModel.audience_type_code == audience_type_code,
                    )
                    .all()
                )
            else:
                result = (
                    db.query(
                        RecommendProductsModel.recsys_model_id.label("id"),
                        RecommendProductsModel.recsys_model_name.label("name"),
                    )
                    .filter(
                        RecommendProductsModel.audience_type_code == audience_type_code
                    )
                    .all()
                )

            return [
                IdWithItem(
                    id=data.id,
                    name=data.name,
                )
                for data in result
            ]
