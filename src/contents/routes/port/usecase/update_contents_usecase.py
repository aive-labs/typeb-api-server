from abc import ABC, abstractmethod

from src.contents.infra.dto.response.contents_response import ContentsResponse
from src.contents.routes.dto.request.contents_create import ContentsCreate
from src.users.domain.user import User


class UpdateContentsUseCase(ABC):

    @abstractmethod
    def exec(
        self, contents_id: int, contents_create: ContentsCreate, user: User
    ) -> ContentsResponse:
        pass
