from fastapi import Depends
from jose import jwt
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

from src.auth.service.auth_service import reuseable_oauth
from src.common.utils.get_env_variable import get_env_variable
from src.core.database import Base
from src.core.exceptions.exceptions import AuthException

db_engine = {}


def get_engine(db_url: str):
    return create_engine(db_url)


def get_session(engine):
    return scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))


def prefix_db_url(db_name: str):
    db_url = get_env_variable("prefix_db_url")
    return f"{db_url}/{db_name}"


def get_db(token: str = Depends(reuseable_oauth)):
    secret_key = get_env_variable("secret_key")
    algorithm = get_env_variable("hash_algorithm")
    payload = jwt.decode(token, secret_key, algorithms=[algorithm])
    mall_id = payload.get("mall_id")
    if mall_id is None:
        raise AuthException(detail={"message": "계정에 해당하는 쇼핑몰 정보를 찾지 못하였습니다."})

    mall_id = "aivelabsdb" if mall_id == "aivelabs" else mall_id
    print(f"[DB] Get DB Connection for {mall_id}")
    if mall_id in db_engine:
        # 기존 엔진 반환
        print(f"[DB] Returning existing engine for mall_id: {mall_id}")
        engine = db_engine[mall_id]
    else:
        # 새로운 엔진 생성 및 등록
        print(f"[DB] Creating new engine for mall_id: {mall_id}")
        engine = get_engine(prefix_db_url(mall_id))
        db_engine[mall_id] = engine
    print(f"[DB] DB Connection URL: {str(engine.url)}")

    session_local = get_session(engine)
    db = session_local()
    try:
        # print(f"SET search_path TO {mall_id}")
        # session_local.execute(text(f"SET search_path TO {mall_id}"))
        yield db
    finally:
        db.close()


def get_db_for_with_mall_id(mall_id):
    engine = get_engine(prefix_db_url(mall_id))
    Base.metadata.create_all(bind=engine)
    session_local = get_session(engine)
    db = session_local()
    return db
