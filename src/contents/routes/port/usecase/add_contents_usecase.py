from abc import ABC, abstractmethod

from src.contents.routes.dto.request.contents_create import ContentsCreate
from src.users.domain.user import User


class AddContentsUseCase(ABC):
    @abstractmethod
    async def create_contents(self, contents_create: ContentsCreate, user: User):
        pass
