from contextlib import AbstractContextManager
from typing import Callable

from sqlalchemy.orm import Session

from src.common.utils.model_converter import ModelConverter
from src.messages.infra.entity.ppurio_message_result_entity import (
    PpurioMessageResultEntity,
)
from src.messages.routes.dto.ppurio_message_result import PpurioMessageResult


class PpurioMessageRepository:

    def __init__(self, db: Callable[..., AbstractContextManager[Session]]):
        """_summary_

        Args:
            db (Callable[..., AbstractContextManager[Session]]):
            - Callable 호출 가능한 객체
            - AbstractContextManager[Session]: 세션 객체를 반환하는 컨텍스트 관리자
            - Session: SQLAlchemy의 세션 객체

        """
        self.db = db

    def save_message_result(self, result: PpurioMessageResult):
        with self.db() as db:
            new_entity = ModelConverter.model_to_entity(
                result, PpurioMessageResultEntity
            )
            db.add(new_entity)
            db.commit()
