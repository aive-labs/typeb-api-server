from abc import ABC, abstractmethod

from src.contents.domain.contents import Contents
from src.contents.routes.dto.request.contents_create import ContentsCreate
from src.users.domain.user import User


class UpdateContentsUseCase(ABC):

    @abstractmethod
    def exec(
        self, contents_id: int, contents_create: ContentsCreate, user: User
    ) -> Contents:
        pass
