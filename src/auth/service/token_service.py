from datetime import datetime, timedelta, timezone
from typing import Any, Union

import pytz
from jose import jwt

from src.auth.routes.dto.response.token_response import TokenResponse
from src.auth.utils.jwt_settings import JwtSettings
from src.common.utils.get_env_variable import get_env_variable
from src.users.domain.user import User


class TokenService:
    SECRET_KEY = get_env_variable("secret_key")
    ALGORITHM = get_env_variable("hash_algorithm")
    ACCESS_TOKEN_EXPIRE_MINUTES = int(get_env_variable("access_token_expires_in"))
    REFRESH_TOKEN_EXPIRE_MINUTES = int(get_env_variable("refresh_token_expires_in"))

    def __init__(self):
        self.jwt_setting = JwtSettings()

    def create_token(self, user: User, mall_id):
        payload = {
            "email": user.email,
            "department": user.department_name,
            "mall_id": mall_id,
            "language": user.language,
            "permissions": user.permissions,
            "role": user.role_id,
        }

        access_token = self.create_access_token(payload)
        refresh_token, _ = self.create_refresh_token(
            email=user.email,
            user_id=str(user.user_id),
        )

        return TokenResponse(
            access_token=access_token,
            access_token_expires_in=self.ACCESS_TOKEN_EXPIRE_MINUTES,
            refresh_token=refresh_token,
            token_type="Bearer",
            refresh_token_expires_in=self.REFRESH_TOKEN_EXPIRE_MINUTES,
        )

    def create_access_token(self, data: dict):
        to_encode = data.copy()
        expire = datetime.now(timezone.utc) + timedelta(minutes=self.ACCESS_TOKEN_EXPIRE_MINUTES)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, self.SECRET_KEY, algorithm=self.ALGORITHM)
        return encoded_jwt

    def create_refresh_token(
        self,
        email: Union[str, Any],
        user_id: Union[str, Any],
    ) -> tuple[str, str]:
        # KST 기준 토큰 만료시간 계산. datetime.now()
        expires_in = datetime.now() + timedelta(minutes=self.jwt_setting.refresh_token_expired)

        local_timezone = pytz.timezone("UTC")

        # astimezone: UTC 시간으로 변환 & replace:초단위까지 표시 & isoformat:aware datetime으로 변경
        expires_in = expires_in.astimezone(local_timezone).replace(microsecond=0).isoformat()

        payload = {
            "email": email,
            "user_id": user_id,
            "expires": expires_in,
        }
        encoded_jwt = jwt.encode(claims=payload, key=self.jwt_setting.secret_key, algorithm="HS256")
        return encoded_jwt, expires_in
