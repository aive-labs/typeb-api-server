from abc import ABC, abstractmethod
from typing import List

from users.routes.dto.request.user_create_request import UserCreate
from users.routes.dto.response.user_response import UserResponse


class BaseUserService(ABC):
    @abstractmethod
    def register_user(self, user_create: UserCreate) -> UserResponse:
        pass

    @abstractmethod
    def update_user(self, user_id: int, user):
        pass

    @abstractmethod
    def delete_user(self, user_id: int):
        pass

    @abstractmethod
    def get_user_by_id(self, user_id: int) -> UserResponse:
        pass

    @abstractmethod
    def get_all_users(self) -> List[UserResponse]:
        pass
