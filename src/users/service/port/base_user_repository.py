from abc import ABC, abstractmethod


class BaseUserRepository(ABC):
    @abstractmethod
    def register_user(self, user):
        pass

    @abstractmethod
    def update_user(self, user_id: int, user):
        pass

    @abstractmethod
    def delete_user(self, user_id: int):
        pass

    @abstractmethod
    def get_user_by_id(self, user_id: int):
        pass

    @abstractmethod
    def get_user_by_email(self, email: str):
        pass

    @abstractmethod
    def get_all_users(self):
        pass
