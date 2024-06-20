from collections.abc import Callable
from contextlib import AbstractContextManager
from typing import List

from sqlalchemy import func, update
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session

from src.auth.enums.cafe24_data_migration_status import CAFE24DataMigrationStatus
from src.auth.infra.dto.cafe24_mall_info import Cafe24MallInfo
from src.auth.infra.dto.cafe24_state_token import Cafe24StateToken
from src.auth.infra.dto.cafe24_token import Cafe24TokenData
from src.auth.infra.entity.cafe24_integration_entity import Cafe24IntegrationEntity
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
            insert_statement = insert(Cafe24IntegrationEntity).values(
                user_id=user_id, mall_id=mall_id, state_token=state_token
            )

            upsert_statement = insert_statement.on_conflict_do_update(
                index_elements=["mall_id"],  # conflict 대상 열
                set_={"user_id": user_id, "state_token": state_token},  # 업데이트할 열
            )

            db.execute(upsert_statement)
            db.commit()

    def is_existing_state_token(self, state_token: str) -> Cafe24StateToken:
        with self.db() as db:
            token = (
                db.query(Cafe24IntegrationEntity)
                .filter(Cafe24IntegrationEntity.state_token == state_token)
                .first()
            )

            if not token:
                raise NotFoundError("해당 state은 유효하지 않습니다.")

            return Cafe24StateToken(
                mall_id=token.mall_id, state_token=token.state_token
            )

    def get_cafe24_info_by_user_id(self, user_id: str):
        with self.db() as db:
            entities: List[Cafe24IntegrationEntity] = (
                db.query(Cafe24IntegrationEntity)
                .filter(Cafe24IntegrationEntity.user_id == user_id)
                .all()
            )

            if len(entities) == 0:
                return None
            elif len(entities) > 1:
                raise Exception("user_id는 1개만 가질 수 있습니다.")
            else:
                entity = entities[0]
                return Cafe24MallInfo(
                    mall_id=entity.mall_id,
                    user_id=str(entity.user_id),
                    scopes=entity.scopes.split(","),
                    shop_no=entity.shop_no,
                )

    def get_state_token(self, state_token: str) -> Cafe24StateToken:
        with self.db() as db:
            entity = (
                db.query(Cafe24IntegrationEntity)
                .filter(Cafe24IntegrationEntity.state_token == state_token)
                .first()
            )

            if not entity:
                raise NotFoundError("state token에 해당하는 데이터를 찾지 못했습니다.")

            return Cafe24StateToken(
                mall_id=entity.mall_id, state_token=entity.state_token
            )

    def save_tokens(self, cafe24_tokens: Cafe24TokenData):
        with self.db() as db:
            entity = (
                db.query(Cafe24IntegrationEntity)
                .filter_by(mall_id=cafe24_tokens.mall_id)
                .first()
            )

            if not entity:
                raise NotFoundError("해당 state 토큰을 찾을 수 없습니다.")

            statement = (
                update(Cafe24IntegrationEntity)
                .where(Cafe24IntegrationEntity.mall_id == cafe24_tokens.mall_id)
                .values(
                    access_token=cafe24_tokens.access_token,
                    access_token_expired_at=cafe24_tokens.expires_at,
                    refresh_token=cafe24_tokens.refresh_token,
                    refresh_token_expired_at=cafe24_tokens.refresh_token_expires_at,
                    scopes=",".join(cafe24_tokens.scopes),
                    shop_no=cafe24_tokens.shop_no,
                    cafe24_user_id=cafe24_tokens.user_id,
                    data_migration_status=CAFE24DataMigrationStatus.PENDING.value,
                    updated_dt=func.now(),
                )
            )

            db.execute(statement)
            db.commit()
