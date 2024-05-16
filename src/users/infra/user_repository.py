from typing import List, Optional
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
        user: User = user_create.to_user()
        user_entity: UserEntity = self.user_sqlalchemy.register_user(user.to_entity())
        return User.from_entity(user_entity=user_entity)

    def update_user(self, user_id: int, user):
        raise NotImplementedError

    def delete_user(self, user_id: int):
        # self.user_sqlalchemy.de
        pass

    def get_user_by_id(self, user_id: int) -> Optional[User]:
        user_entity: UserEntity = self.user_sqlalchemy.get_user_by_id(user_id)
        return User.from_entity(user_entity=user_entity)

    def get_all_users(self) -> List[User]:
        user_entities = self.user_sqlalchemy.get_all_users()
        return [User.from_entity(user_entity) for user_entity in user_entities]

    def get_user_by_email(self, email: str) -> Optional[User]:
        user = self.user_sqlalchemy.find_user_by_email(email)
        return user
