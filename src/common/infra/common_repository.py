from contextlib import AbstractContextManager
from typing import Callable

from sqlalchemy.orm import Session

from src.common.infra.entity.recsys_models_entity import RecsysModelsEntity
from src.search.routes.dto.id_with_item_response import IdWithItemDescription
from src.common.domain.recsys_models import RecsysModels


class CommonRepository:
    def __init__(self, db: Callable[..., AbstractContextManager[Session]]):
        """_summary_

        Args:
            db (Callable[..., AbstractContextManager[Session]]):
            - Callable 호출 가능한 객체
            - AbstractContextManager[Session]: 세션 객체를 반환하는 컨텍스트 관리자
            - Session: SQLAlchemy의 세션 객체

        """
        self.db = db


    def get_recsys_model(self, recsys_model_id: int) -> RecsysModels: 
        with self.db() as db:

            result = db.query(
                RecsysModelsEntity
            ).filter(
                RecsysModelsEntity.recsys_model_id == recsys_model_id
                ).first()
            
            return result