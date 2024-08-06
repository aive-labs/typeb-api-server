from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from src.auth.routes.dto.response.token_response import TokenResponse
from src.auth.service.token_service import TokenService
from src.core.exceptions.exceptions import (
    AuthException,
    NotFoundException,
)
from src.users.service.port.base_user_repository import BaseUserRepository

reuseable_oauth = OAuth2PasswordBearer(tokenUrl="/users/signin", scheme_name="JWT")

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class AuthService:
    def __init__(self, token_service: TokenService, user_repository: BaseUserRepository):
        self.token_service = token_service
        self.user_repository = user_repository

    def login(self, login_id: str, password: str, mall_id: str, db: Session) -> TokenResponse:
        # 사용자 존재 유무 확인
        user = self.user_repository.get_user_by_email(login_id, db)
        if user is None:
            raise NotFoundException(detail={"message": "가입되지 않은 사용자 입니다."})

        # 패스워드 일치 확인
        if not self.verify_password(password, user.password):
            raise AuthException(detail={"message": "패스워드가 일치하지 않습니다."})

        # 토큰 발급
        token_response = self.token_service.create_token(user, mall_id)

        # TODO: refresh_token save

        return token_response

    def get_password_hash(self, password: str) -> str:
        return pwd_context.hash(password)

    def verify_password(self, plain_password, hashed_password) -> bool:
        result = pwd_context.verify(plain_password, hashed_password)
        return result
