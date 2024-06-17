from abc import ABC, abstractmethod

from src.audiences.routes.dto.response.audience_stat_info import AudienceStatsInfo
from src.audiences.routes.dto.response.audiences import AudienceResponse
from src.users.domain.user import User


class GetAudienceUseCase(ABC):
    @abstractmethod
    def get_all_audiences(
        self, user: User, is_exclude: bool | None = None
    ) -> AudienceResponse:
        pass

    @abstractmethod
    def get_audience_details(self, audience_id: str) -> AudienceStatsInfo:
        pass
