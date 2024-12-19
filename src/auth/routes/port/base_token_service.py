from abc import ABC, abstractmethod

from src.user.domain.user import User


class BaseTokenService(ABC):
    @abstractmethod
    def create_token(self, user: User):
        pass

    @abstractmethod
    def create_access_token(self, data: dict):
        pass

    @abstractmethod
    def create_refresh_token(self, email: str):
        pass
