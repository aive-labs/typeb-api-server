from abc import ABC, abstractmethod

from src.users.domain.user import User


class GetAudienceUsecase(ABC):

    @abstractmethod
    def get_all_audiences(self, user: User, is_exclude: bool | None = None):
        pass

    @abstractmethod
    def get_audience_details(self, audience_id: str):
        pass
