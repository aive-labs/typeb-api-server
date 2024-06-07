from abc import ABC, abstractmethod

from fastapi import UploadFile

from src.contents.routes.dto.request.creatives_create import CreativeCreate


class AddCreativesUseCase(ABC):
    @abstractmethod
    async def upload_image(self, asset_data: CreativeCreate, files: list[UploadFile]):
        pass
