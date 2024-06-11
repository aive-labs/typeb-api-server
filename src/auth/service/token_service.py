from datetime import datetime, timedelta, timezone
from typing import Any, Union

import pytz
from jose import jwt

from src.auth.routes.dto.response.token_response import TokenResponse
from src.auth.utils.jwt_settings import JwtSettings
from src.users.domain.user import User

SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


class TokenService:
    def __init__(self):
        self.jwt_setting = JwtSettings()

    def create_token(self, user: User):
        payload = {
            "email": user.email,
            "department": user.department_name,
            "language": user.language,
            "permissions": user.permissions,
            "role": user.role_id,
        }

        access_token = self.create_access_token(payload)
        refresh_token = self.create_refresh_token(
            subject=user.email,
            subject_userid=str(user.user_id),
        )

        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="Bearer",
            expires_in=ACCESS_TOKEN_EXPIRE_MINUTES,
        )

    def create_access_token(self, data: dict):
        to_encode = data.copy()
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=ACCESS_TOKEN_EXPIRE_MINUTES
        )
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt

    def create_refresh_token(
        self,
        subject: Union[str, Any],
        subject_userid: Union[str, Any],
    ) -> str:
        # KST 기준 토큰 만료시간 계산. datetime.now()
        expires_in = datetime.now() + timedelta(
            minutes=self.jwt_setting.refresh_token_expired
        )

        local_timezone = pytz.timezone("UTC")

        # astimezone: UTC 시간으로 변환 & replace:초단위까지 표시 & isoformat:aware datetime으로 변경
        expires_in = (
            expires_in.astimezone(local_timezone).replace(microsecond=0).isoformat()
        )

        payload = {
            "email": subject,
            "user_id": subject_userid,
            "expires": expires_in,
        }
        encoded_jwt = jwt.encode(
            claims=payload, key=self.jwt_setting.secret_key, algorithm="HS256"
        )
        return encoded_jwt
