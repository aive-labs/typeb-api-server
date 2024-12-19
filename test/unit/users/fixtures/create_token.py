from datetime import datetime, timedelta, timezone

from jose import jwt

from src.common.utils.get_env_variable import get_env_variable


def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=60)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode, get_env_variable("secret_key"), algorithm=get_env_variable("hash_algorithm")
    )
    return encoded_jwt
