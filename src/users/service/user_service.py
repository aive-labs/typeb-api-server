from sqlalchemy.orm import Session

from src.core.exceptions.exceptions import DuplicatedException, NotFoundException
from src.users.domain.user import User
from src.users.routes.dto.request.user_create import UserCreate
from src.users.routes.dto.request.user_modify import UserModify
from src.users.routes.dto.response.user_response import UserResponse
from src.users.routes.port.base_user_service import BaseUserService
from src.users.service.port.base_user_repository import BaseUserRepository


class UserService(BaseUserService):
    def __init__(self, user_repository: BaseUserRepository):
        self.user_repository = user_repository

    def register_user(self, user_create: UserCreate, db: Session) -> UserResponse:
        # 1. 가입 아이디로 사용자 존재 유무 확인
        existing_user = self.user_repository.is_existing_user(user_create.email, db)

        if existing_user:
            raise DuplicatedException(detail={"message": "동일한 이메일이 존재합니다."})

        # 2. 회원 가입 진행
        saved_user: User = self.user_repository.register_user(user_create, db)

        return UserResponse(**saved_user.model_dump())

    def update_user(self, user_modify: UserModify, db: Session):
        self.user_repository.update_user(user_modify, db)

    def delete_user(self, user_id: int, db: Session):
        self.user_repository.delete_user(user_id, db)

    def get_user_by_id(self, user_id: int, db: Session) -> UserResponse:
        user: User | None = self.user_repository.get_user_by_id(user_id, db)

        if user is None:
            raise NotFoundException(detail={"message": "사용자를 찾지 못했습니다."})

        return UserResponse(**user.model_dump())

    def get_all_users(self, db: Session) -> list[UserResponse]:
        users = self.user_repository.get_all_users(db)
        user_responses = [UserResponse(**user.model_dump()) for user in users]
        return user_responses
