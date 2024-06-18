from abc import ABC, abstractmethod

from src.contents.domain.contents import Contents
from src.contents.routes.dto.request.contents_create import ContentsCreate
from src.users.domain.user import User


class AddContentsUseCase(ABC):
    @abstractmethod
    def create_contents(self, contents_create: ContentsCreate, user: User) -> Contents:
        pass
