import logging
import os
from collections.abc import Callable
from contextlib import AbstractContextManager, contextmanager

from pydantic_settings import BaseSettings
from sqlalchemy import MetaData, create_engine, orm
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session

# SQLAlchemy의 로깅 수준을 디버그로 설정
logging.basicConfig()
logging.getLogger("sqlalchemy.engine").setLevel(logging.INFO)


class DBSettings(BaseSettings):
    # app_name: str = "tt"
    env: str
    # drivername: str
    # host: str
    # dbuser: str
    # password: str
    # database: str
    # port: str
    database_url: str

    class Config:
        env_type = os.environ.get("ENV_TYPE")

        if not env_type:
            env_file = "../config/env/.env"
        elif env_type == "test_code":
            env_file = "../config/env/test.env"
        elif env_type == "nepa-stg":
            env_file = "../config/env/local_nepa.env"
        else:
            env_file = f"../config/env/{env_type}.env"

        print(f"env_file: {env_file}")
        env_file_encoding = "utf-8"


def get_db_url():
    db_settings = DBSettings()  # type: ignore
    print(db_settings.env)
    print(f"database_connection: {db_settings.database_url}")
    return db_settings.database_url


## check schema name for deployment
metaobj = MetaData(schema="aivelabs_sv")
BaseModel = declarative_base(metadata=metaobj)


class Database:
    def __init__(self, db_url: str) -> None:
        self._engine = create_engine(
            db_url, pool_recycle=60, pool_size=10, max_overflow=20, echo=True
        )
        self._session_factory = orm.scoped_session(
            session_factory=orm.sessionmaker(
                autocommit=False,
                autoflush=False,
                bind=self._engine,
            ),
        )

    def create_database(self) -> None:
        BaseModel.metadata.create_all(self._engine)  # type: ignore

    @contextmanager  # type: ignore
    def session(self) -> Callable[..., AbstractContextManager[Session]]:  # type: ignore
        session: Session = self._session_factory()
        try:
            yield session  # type: ignore
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()
