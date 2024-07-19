from sqlalchemy.orm import Session

from src.core.exceptions.exceptions import NotFoundException
from src.search.routes.dto.send_user_response import SendUserResponse
from src.users.domain.user import User
from src.users.infra.entity.user_entity import UserEntity
from src.users.infra.user_sqlalchemy import UserSqlAlchemy
from src.users.routes.dto.request.user_create import UserCreate
from src.users.routes.dto.request.user_modify import UserModify
from src.users.service.port.base_user_repository import BaseUserRepository


class UserRepository(BaseUserRepository):

    def __init__(self, user_sqlalchemy: UserSqlAlchemy):
        self.user_sqlalchemy = user_sqlalchemy

    def register_user(self, user_create: UserCreate, db: Session) -> User:
        user: User = user_create.to_user()

        return self.user_sqlalchemy.register_user(user.to_entity(), user.to_password_entity(), db)

    def update_user(self, user_modify: UserModify, db: Session):
        self.user_sqlalchemy.update_user(user_modify, db)

    def delete_user(self, user_id: int, db: Session):
        pass

    def get_user_by_id(self, user_id: int, db: Session) -> User | None:
        user_entity: UserEntity = self.user_sqlalchemy.get_user_by_id(user_id, db)
        return User.from_entity(user_entity=user_entity)

    def get_all_users(self, db: Session) -> list[User]:
        user_entities = self.user_sqlalchemy.get_all_users(db)
        return [User.from_entity(user_entity) for user_entity in user_entities]

    def get_user_by_email(self, email: str, db: Session) -> User | None:
        user_info = self.user_sqlalchemy.find_user_by_email(email, db)

        if user_info is None:
            raise NotFoundException(detail={"message": "해당하는 사용자를 찾지 못하였습니다."})

        user = User.from_entity(user_info[0])
        user.password = user_info[1]

        return user

    def is_existing_user(self, email: str, db: Session) -> bool:
        user_info = self.user_sqlalchemy.find_user_by_email(email, db)
        if user_info:
            return True

        return False

    def get_send_users(self, db: Session, keyword=None) -> list[SendUserResponse]:
        return self.user_sqlalchemy.get_send_user(db, keyword)
