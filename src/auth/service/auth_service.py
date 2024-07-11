from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from src.auth.routes.dto.response.token_response import TokenResponse
from src.auth.service.token_service import TokenService
from src.core.exceptions.exceptions import (
    AuthException,
    CredentialException,
    NotFoundException,
)
from src.users.service.port.base_user_repository import BaseUserRepository

reuseable_oauth = OAuth2PasswordBearer(tokenUrl="/users/signin", scheme_name="JWT")

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


class AuthService:
    def __init__(self, token_service: TokenService, user_repository: BaseUserRepository):
        self.token_service = token_service
        self.user_repository = user_repository

    def login(self, login_id: str, password: str, db: Session) -> TokenResponse:
        # 사용자 존재 유무 확인
        user = self.user_repository.get_user_by_email(login_id, db)
        if user is None:
            raise NotFoundException(detail={"message": "가입되지 않은 사용자 입니다."})

        # 패스워드 일치 확인
        if not self.verify_password(password, user.password):
            raise AuthException(detail={"message": "패스워드가 일치하지 않습니다."})

        # 토큰 발급
        token_response = self.token_service.create_token(user)

        # TODO: refresh_token save

        return token_response

    def get_password_hash(self, password: str) -> str:
        return pwd_context.hash(password)

    def verify_password(self, plain_password, hashed_password) -> bool:
        result = pwd_context.verify(plain_password, hashed_password)
        return result

    def get_current_user(
        self, refresh_token: str, db: Session, token: str = Depends(reuseable_oauth)
    ):
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            email = payload.get("email")
            if email is None:
                raise AuthException("해당하는 이메일을 찾지 못하였습니다.")
        except JWTError as e:
            raise CredentialException(detail={"message": "유효하지 않은 토큰입니다."}) from e

        user = self.user_repository.get_user_by_email(email, db)
        if user is None:
            raise NotFoundException(detail={"message": "해당하는 이메일을 찾지 못하였습니다."})

        return user

    def get_new_token(self, refresh_token: str, db: Session) -> TokenResponse:
        user = self.get_current_user(refresh_token, db)
        token_response = self.token_service.create_token(user)
        # TODO: refresh_token save

        return token_response
