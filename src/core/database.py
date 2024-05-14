import os
from sqlalchemy import create_engine
from pydantic_settings import BaseSettings

from contextlib import AbstractContextManager, contextmanager
from typing import Any, Callable

from sqlalchemy import create_engine, orm
from sqlalchemy.ext.declarative import as_declarative, declared_attr
from sqlalchemy.orm import Session


class DBSettings(BaseSettings):
    app_name: str = "tt"
    env: str
    drivername: str
    host: str
    dbuser: str
    password: str
    database: str
    port: str

    class Config:
        env_type = os.environ.get("ENV_TYPE")

        if not env_type:
            env_file = "../config/env/.env"
        elif env_type == "nepa-stg":
            env_file = "../config/env/local_nepa.env"
        else:
            env_file = f"../config/env/{env_type}.env"

        env_file_encoding = "utf-8"


def get_db_settings():
    db_settings = DBSettings()
    return {
        "drivername": db_settings.drivername,
        "host": db_settings.host,
        "username": db_settings.dbuser,
        "password": db_settings.password,
        "database": db_settings.database,
        "port": db_settings.port,
    }


@as_declarative()
class BaseModel:
    id: Any
    __name__: str
    __table_args__ = {"schema": "aivelabs_sv"}

    # Generate __tablename__ automatically
    @declared_attr
    def __tablename__(cls) -> str:
        return cls.__name__.lower()


class Database:
    def __init__(self, db_url: str) -> None:
        self._engine = create_engine(
            db_url, pool_recycle=60, pool_size=10, max_overflow=20, echo=True
        )
        self._session_factory = orm.scoped_session(
            orm.sessionmaker(
                autocommit=False,
                autoflush=False,
                bind=self._engine,
            ),
        )

    def create_database(self) -> None:
        BaseModel.metadata.create_all(self._engine)

    @contextmanager
    def session(self) -> Callable[..., AbstractContextManager[Session]]:
        session: Session = self._session_factory()
        try:
            yield session
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()
