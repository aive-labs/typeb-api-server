import os
from collections.abc import Callable
from contextlib import AbstractContextManager, contextmanager

from pydantic_settings import BaseSettings
from sqlalchemy import MetaData, create_engine, orm
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session, scoped_session, sessionmaker

from src.common.utils.get_env_variable import get_env_variable
from src.core.schema import schema_context


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
        Base.metadata.create_all(self._engine)

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
        schema_name = schema_context.get()
        print(f"[get_db_session] {schema_name}")
        # print(f"[get_db_session] SET search_path TO {schema_name}")
        # session.execute(text(f"SET search_path TO {schema_name}"))
        print("--------")

        yield session


def get_engine(db_url: str):
    return create_engine(db_url)


def get_session(engine):
    return scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))


def prefix_db_url(db_name: str):
    db_url = get_env_variable("prefix_db_url")
    return f"{db_url}/{db_name}"


def get_db():
    db_name = "aivelabsdb"
    engine = get_engine(prefix_db_url(db_name))
    session_local = get_session(engine)
    Base.metadata.create_all(bind=engine)
    db = session_local()
    try:
        yield db
    finally:
        db.close()
