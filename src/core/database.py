import os
from collections.abc import Callable
from contextlib import AbstractContextManager, contextmanager

import psycopg2
from pydantic_settings import BaseSettings
from sqlalchemy import MetaData, create_engine, orm
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session

from src.common.utils.get_env_variable import get_env_variable
from src.core.exceptions.exceptions import NotFoundException


class DBSettings(BaseSettings):
    env: str
    database_url: str

    class Config:
        env_type = os.environ.get("ENV_TYPE")
        env_file_encoding = "utf-8"
        extra = "ignore"

        if not env_type:
            env_file = "config/env/.env"
        elif env_type == "test_code":
            env_file = "config/env/test.env"
        else:
            env_file = f"config/env/{env_type}.env"

        print(f"env_file: {env_file}")


def get_db_url():
    db_settings = DBSettings()  # pyright: ignore [reportCallIssue]
    print(f"database_connection: {db_settings.database_url}")
    return db_settings.database_url


# meta_obj = MetaData()
meta_obj = MetaData(schema="aivelabs_sv")
Base = declarative_base(metadata=meta_obj)


class Database:
    def __init__(self, db_url: str) -> None:
        self._engine = create_engine(
            db_url, pool_recycle=60, pool_size=10, max_overflow=20, echo=False
        )
        self._session_factory = orm.scoped_session(
            session_factory=orm.sessionmaker(
                autocommit=False,
                autoflush=False,
                bind=self._engine,
            ),
        )
        self._create_database()

    def _create_database(self) -> None:
        # SQLAlchemy의 create_all 메서드는 테이블이 없는 경우에만 테이블을 생성. 기존 테이블의 스키마를 업데이트하지 않음
        print(f"CREATING DATABASE: {self._engine}")

        default_url = self._engine.url
        base_db_name = str(default_url).split("/")[-1]

        if base_db_name == "common":
            print(f"DATABASE: {base_db_name} SCHEMA: {Base.metadata.schema}")
        else:
            print(f"DATABASE: {base_db_name}")
            Base.metadata.create_all(bind=self._engine)

    @contextmanager  # type: ignore
    def session(self) -> Callable[..., AbstractContextManager[Session]]:  # type: ignore
        session: Session = self._session_factory()
        try:
            yield session  # pyright: ignore [reportReturnType]
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()


db = Database(get_db_url())


# 의존성 주입을 위한 함수
def get_db_session():
    with db.session() as session:
        yield session


def get_mall_id_by_user(user_id: str) -> str:
    user_db_conn = psycopg2.connect(
        dbname=get_env_variable("user_db_name"),
        user=get_env_variable("user_db_user"),
        password=get_env_variable("user_db_password"),
        host=get_env_variable("user_db_host"),
        port=get_env_variable("user_db_port"),
    )

    with user_db_conn.cursor() as cursor:
        cursor.execute(
            """
            select *
            from public.clients
            where user_id = %s
            """,
            (user_id,),
        )

        result = cursor.fetchone()
        if result is None:
            raise NotFoundException(detail={"message": "사용자 정보를 찾을 수 없습니다."})

        mall_id = result[1]
        if mall_id is None:
            raise NotFoundException(detail={"message": "사용자 정보를 찾을 수 없습니다."})
        return mall_id


def get_mall_url_by_user(user_id: str) -> str:
    user_db_conn = psycopg2.connect(
        dbname=get_env_variable("user_db_name"),
        user=get_env_variable("user_db_user"),
        password=get_env_variable("user_db_password"),
        host=get_env_variable("user_db_host"),
        port=get_env_variable("user_db_port"),
    )

    with user_db_conn.cursor() as cursor:
        cursor.execute(
            """
            select mall_url
            from public.clients
            where user_id = %s
            """,
            (user_id,),
        )

        result = cursor.fetchone()
        if result is None:
            raise NotFoundException(detail={"message": "사용자 정보를 찾을 수 없습니다."})

        return result[0]
