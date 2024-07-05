from abc import ABC, abstractmethod

from sqlalchemy.orm import Session

from src.audiences.domain.audience import Audience
from src.audiences.routes.dto.response.audience_stat_info import AudienceStatsInfo
from src.audiences.routes.dto.response.audiences import AudienceResponse
from src.audiences.routes.dto.response.default_exclude_audience import (
    DefaultExcludeAudience,
)
from src.users.domain.user import User


class GetAudienceUseCase(ABC):
    @abstractmethod
    def get_all_audiences(
        self, user: User, db: Session, is_exclude: bool | None = None
    ) -> AudienceResponse:
        pass

    @abstractmethod
    def get_audience_stat_details(
        self, audience_id: str, db: Session
    ) -> AudienceStatsInfo:
        pass

    @abstractmethod
    def get_audience_details(self, audience_id: str, db: Session) -> Audience:
        pass

    @abstractmethod
    def get_default_exclude(
        self, user: User, db: Session
    ) -> list[DefaultExcludeAudience]:
        pass
