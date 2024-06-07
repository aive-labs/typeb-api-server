from datetime import datetime, timedelta, timezone

from fastapi.security import OAuth2PasswordBearer
from jose import jwt

from src.auth.routes.dto.response.token_response import TokenResponse
from src.users.domain.user import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


class TokenService:

    def __init__(self):
        pass

    def create_token(self, user: User):
        payload = {
            'email': user.email,
            'department': user.department_name,
            'language': user.language,
            'permissions': user.permissions,
            'role': user.role_id
        }

        access_token = self.create_access_token(payload)
        refresh_token = self.create_refresh_token(email=user.email)

        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type='Bearer',
            expires_in=ACCESS_TOKEN_EXPIRE_MINUTES)

    def create_access_token(self, data: dict):
        to_encode = data.copy()
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt

    def create_refresh_token(self, email: str):
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES * 2)
        to_encode = {'email': email, "exp": expire}
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt
