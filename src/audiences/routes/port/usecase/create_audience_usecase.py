from abc import ABC, abstractmethod

from src.audiences.routes.dto.request.audience_create import AudienceCreate
from src.audiences.routes.dto.response.audience_variable_combinations import (
    DataType,
    PredefinedVariable,
)
from src.users.domain.user import User


class CreateAudienceUseCase(ABC):
    @abstractmethod
    def create_audience(
        self,
        audience_create: AudienceCreate,
        user: User,
    ) -> str:
        pass

    @abstractmethod
    def get_audience_variable_combinations(
        self, user: User
    ) -> list[PredefinedVariable]:
        pass

    @abstractmethod
    def get_option_items(self) -> list[DataType]:
        pass
