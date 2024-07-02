from abc import ABC, abstractmethod

from src.users.domain.user import User


class GetCampaignUseCase(ABC):
    @abstractmethod
    def get_campaigns(self, start_date: str, end_date: str, user: User):
        pass
