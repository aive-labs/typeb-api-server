
from core.exceptions import DuplicatedError, NotFoundError
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from users.domain.user import User
from users.routes.dto.request.user_create_request import UserCreate
from users.routes.dto.response.user_response import UserResponse
from users.routes.port.base_user_service import BaseUserService
from users.service.port.base_user_repository import BaseUserRepository

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

class UserService(BaseUserService):

    def __init__(self, user_repository: BaseUserRepository):
        self.user_repository = user_repository

    def register_user(self, user_create: UserCreate) -> UserResponse:

        # 1. 가입 아이디로 사용자 존재 유무 확인
        existing_user = self.user_repository.get_user_by_email(user_create.email)

        if existing_user:
            raise DuplicatedError("동일한 이메일이 존재합니다.")

        # 2. 회원 가입 진행
        saved_user: User = self.user_repository.register_user(user_create)

        return UserResponse(**saved_user.model_dump())

    def update_user(self, user_id: int, user):
        raise NotImplementedError

    def delete_user(self, user_id: int):
        self.user_repository.delete_user(user_id)

    def get_user_by_id(self, user_id: int) -> UserResponse:
        user: User | None = self.user_repository.get_user_by_id(user_id)

        if user is None:
            raise NotFoundError("사용자를 찾지 못했습니다.")

        return UserResponse(**user.model_dump())

    def get_all_users(self) -> list[UserResponse]:
        users = self.user_repository.get_all_users()
        user_responses = [UserResponse(**user.model_dump()) for user in users]
        return user_responses
