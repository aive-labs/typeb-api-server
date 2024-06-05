from collections.abc import Callable
from contextlib import AbstractContextManager

from sqlalchemy import func, update
from sqlalchemy.orm import Session

from src.auth.infra.dto.cafe24_state_token import Cafe24StateToken
from src.auth.infra.dto.cafe24_token import Cafe24TokenData
from src.auth.infra.entity.cafe24_token_entity import Cafe24TokenEntity
from src.core.exceptions import NotFoundError


class Cafe24SqlAlchemyRepository:
    def __init__(self, db: Callable[..., AbstractContextManager[Session]]):
        """_summary_

        Args:
            db (Callable[..., AbstractContextManager[Session]]):
            - Callable 호출 가능한 객체
            - AbstractContextManager[Session]: 세션 객체를 반환하는 컨텍스트 관리자
            - Session: SQLAlchemy의 세션 객체

        """
        self.db = db

    def insert_basic_info(self, user_id: str, mall_id: str, state_token: str):
        with self.db() as db:
            entity = Cafe24TokenEntity(
                user_id=user_id, mall_id=mall_id, state_token=state_token
            )
            db.add(entity)
            db.commit()

    def is_existing_state_token(self, state_token: str) -> Cafe24StateToken:
        with self.db() as db:
            token = (
                db.query(Cafe24TokenEntity)
                .filter(Cafe24TokenEntity.state_token == state_token)
                .first()
            )

            if not token:
                raise NotFoundError("해당 state은 유효하지 않습니다.")

            return Cafe24StateToken(
                mall_id=token.mall_id, state_token=token.state_token
            )

    def save_tokens(self, cafe24_tokens: Cafe24TokenData):
        with self.db() as db:
            entity = (
                db.query(Cafe24TokenEntity)
                .filter_by(mall_id=cafe24_tokens.mall_id)
                .first()
            )

            if not entity:
                raise NotFoundError("해당 state 토큰을 찾을 수 없습니다.")

            statement = (
                update(Cafe24TokenEntity)
                .where(Cafe24TokenEntity.mall_id == cafe24_tokens.mall_id)
                .values(
                    access_token=cafe24_tokens.access_token,
                    access_token_expired_at=cafe24_tokens.expires_at,
                    refresh_token=cafe24_tokens.refresh_token,
                    refresh_token_expired_at=cafe24_tokens.refresh_token_expires_at,
                    scopes=",".join(cafe24_tokens.scopes),
                    shop_no=cafe24_tokens.shop_no,
                    cafe24_user_id=cafe24_tokens.user_id,
                    updated_dt=func.now(),
                )
            )

            db.execute(statement)
            db.commit()
