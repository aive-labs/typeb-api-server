from abc import ABC, abstractmethod

from fastapi import UploadFile

from src.contents.routes.dto.request.contents_create import ContentsCreate
from src.users.domain.user import User


class AddContentsUseCase(ABC):
    @abstractmethod
    def create_contents(self, contet_create: ContentsCreate, user: User, files: UploadFile | None = None):  # type: ignore
        pass
