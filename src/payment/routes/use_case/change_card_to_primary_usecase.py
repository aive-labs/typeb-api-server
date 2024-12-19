from abc import ABC, abstractmethod

from sqlalchemy.orm import Session

from src.core.transactional import transactional
from src.user.domain.user import User


class ChangeCardToPrimaryUseCase(ABC):

    @transactional
    @abstractmethod
    def exec(self, card_id: int, user: User, db: Session):
        pass
