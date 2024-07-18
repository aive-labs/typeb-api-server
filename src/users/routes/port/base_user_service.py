from abc import ABC, abstractmethod

from sqlalchemy.orm import Session

from src.users.routes.dto.request.user_create import UserCreate
from src.users.routes.dto.request.user_modify import UserModify
from src.users.routes.dto.response.user_response import UserResponse


class BaseUserService(ABC):
    @abstractmethod
    def register_user(self, user_create: UserCreate, db: Session) -> UserResponse:
        pass

    @abstractmethod
    def update_user(self, user_modify: UserModify, db: Session):
        pass

    @abstractmethod
    def delete_user(self, user_id: int, db: Session):
        pass

    @abstractmethod
    def get_user_by_id(self, user_id: int, db: Session) -> UserResponse:
        pass

    @abstractmethod
    def get_all_users(self, db: Session) -> list[UserResponse]:
        pass

    @abstractmethod
    def get_send_users(self, permission, db: Session, keyword=None):
        pass
