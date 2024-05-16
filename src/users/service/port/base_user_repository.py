from abc import ABC, abstractmethod
from typing import List, Optional

from src.users.domain.user import User
from users.routes.dto.request.user_create_request import UserCreate


class BaseUserRepository(ABC):
    @abstractmethod
    def register_user(self, user_create: UserCreate) -> User:
        pass

    @abstractmethod
    def update_user(self, user_id: int, user):
        pass

    @abstractmethod
    def delete_user(self, user_id: int):
        pass

    @abstractmethod
    def get_user_by_id(self, user_id: int) -> Optional[User]:
        pass

    @abstractmethod
    def get_user_by_email(self, email: str) -> Optional[User]:
        pass

    @abstractmethod
    def get_all_users(self) -> List[User]:
        pass
