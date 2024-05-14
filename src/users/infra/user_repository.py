from users.domain.user import User
from users.infra.entity.user_entity import UserEntity
from users.infra.user_sqlalchemy import UserSqlAlchemy
from users.routes.dto.request.user_create_request import UserCreate
from users.routes.dto.response.user_response import UserResponse
from users.service.port.base_user_repository import BaseUserRepository
from sqlalchemy.orm import Session


class UserRepository(BaseUserRepository):

    def __init__(self, user_sqlalchemy: UserSqlAlchemy):
        self.user_sqlalchemy = user_sqlalchemy

    def register_user(self, user_create: UserCreate) -> User:
        user = user_create.to_user()
        saved_user = self.user_sqlalchemy.register_user(user.to_entity())
        return saved_user

    def update_user(self, user_id: int, user):
        raise NotImplementedError

    def delete_user(self, user_id: int):
        raise NotImplementedError

    def get_user_by_id(self, user_id: int):
        raise NotImplementedError

    def get_all_users(self):
        raise NotImplementedError

    def get_user_by_email(self, email: str):
        user = self.user_sqlalchemy.find_user_by_email(email)
        print(user)
        return user
