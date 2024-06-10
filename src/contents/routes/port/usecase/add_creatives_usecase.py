from abc import ABC, abstractmethod

from fastapi import UploadFile

from src.contents.routes.dto.request.creatives_create import CreativeCreate
from src.users.domain.user import User


class AddCreativesUseCase(ABC):
    @abstractmethod
    def create_creatives(
        self, asset_data: CreativeCreate, files: list[UploadFile], user: User
    ):
        pass
