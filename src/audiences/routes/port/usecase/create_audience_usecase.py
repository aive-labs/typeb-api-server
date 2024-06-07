from abc import ABC, abstractmethod

from fastapi import BackgroundTasks

from src.audiences.routes.dto.request.audience_create import AudienceCreate
from src.users.domain.user import User


class CreateAudienceUsecase(ABC):
    @abstractmethod
    def create_audience(
        self,
        audience_create: AudienceCreate,
        user: User,
        background_task: BackgroundTasks,
    ):
        pass
