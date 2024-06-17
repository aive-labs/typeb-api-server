from abc import ABC, abstractmethod

from fastapi import BackgroundTasks

from src.audiences.routes.dto.request.audience_create import AudienceCreate
from src.users.domain.user import User


class CreateAudienceUseCase(ABC):
    @abstractmethod
    def create_audience(
        self,
        audience_create: AudienceCreate,
        user: User,
        background_task: BackgroundTasks,
    ) -> str:
        pass

    @abstractmethod
    def get_audience_variable_combinations(self, user: User) -> list[dict]:
        pass
