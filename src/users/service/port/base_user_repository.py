from abc import ABC, abstractmethod

from sqlalchemy.orm import Session

from src.users.domain.user import User
from src.users.routes.dto.request.user_create import UserCreate
from src.users.routes.dto.request.user_modify import UserModify


class BaseUserRepository(ABC):
    @abstractmethod
    def register_user(self, user_create: UserCreate, db: Session) -> User:
        pass

    @abstractmethod
    def update_user(self, user_modify: UserModify, db: Session):
        pass

    @abstractmethod
    def delete_user(self, user_id: int, db: Session):
        pass

    @abstractmethod
    def get_user_by_id(self, user_id: int, db: Session) -> User | None:
        pass

    @abstractmethod
    def get_user_by_email(self, email: str, db: Session) -> User | None:
        pass

    @abstractmethod
    def get_all_users(self, db: Session) -> list[User]:
        pass

    @abstractmethod
    def is_existing_user(self, email: str, db: Session) -> bool:
        pass
