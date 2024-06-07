from src.core.exceptions import NotFoundError
from src.users.domain.user import User
from src.users.infra.entity.user_entity import UserEntity
from src.users.infra.user_sqlalchemy import UserSqlAlchemy
from src.users.routes.dto.request.user_create_request import UserCreate
from src.users.service.port.base_user_repository import BaseUserRepository


class UserRepository(BaseUserRepository):
    def __init__(self, user_sqlalchemy: UserSqlAlchemy):
        self.user_sqlalchemy = user_sqlalchemy

    def register_user(self, user_create: UserCreate) -> User:
        user: User = user_create.to_user()

        return self.user_sqlalchemy.register_user(
            user.to_entity(), user.to_password_entity()
        )

    def update_user(self, user_id: int, user):
        raise NotImplementedError

    def delete_user(self, user_id: int):
        pass

    def get_user_by_id(self, user_id: int) -> User | None:
        user_entity: UserEntity = self.user_sqlalchemy.get_user_by_id(user_id)
        return User.from_entity(user_entity=user_entity)

    def get_all_users(self) -> list[User]:
        user_entities = self.user_sqlalchemy.get_all_users()
        return [User.from_entity(user_entity) for user_entity in user_entities]

    def get_user_by_email(self, email: str) -> User | None:
        user_info = self.user_sqlalchemy.find_user_by_email(email)

        if user_info is None:
            raise NotFoundError("해당하는 사용자를 찾지 못하였습니다.")

        user = User.from_entity(user_info[0])
        user.password = user_info[1]

        return user

    def is_existing_user(self, email: str) -> bool:
        user_info = self.user_sqlalchemy.find_user_by_email(email)
        if user_info:
            return True

        return False
