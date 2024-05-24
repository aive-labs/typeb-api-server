from collections.abc import Callable
from contextlib import AbstractContextManager

from sqlalchemy.orm import Session

from src.contents.infra.entity.contents_entity import ContentsEntity


class ContentsSqlAlchemy:

    def __init__(self, db: Callable[..., AbstractContextManager[Session]]):
        """_summary_

        Args:
            db (Callable[..., AbstractContextManager[Session]]):
            - Callable 호출 가능한 객체
            - AbstractContextManager[Session]: 세션 객체를 반환하는 컨텍스트 관리자
            - Session: SQLAlchemy의 세션 객체

        """
        self.db = db

    def add_contents(self, contents: ContentsEntity):
        with self.db() as db:
            db.add(contents)
            db.commit()
