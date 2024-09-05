from abc import ABC, abstractmethod

from sqlalchemy.orm import Session

from src.contents.infra.dto.response.contents_response import ContentsResponse
from src.contents.routes.dto.request.contents_create import ContentsCreate
from src.core.transactional import transactional
from src.users.domain.user import User


class AddContentsUseCase(ABC):

    @transactional
    @abstractmethod
    def create_contents(
        self, contents_create: ContentsCreate, user: User, db: Session
    ) -> ContentsResponse:
        pass
