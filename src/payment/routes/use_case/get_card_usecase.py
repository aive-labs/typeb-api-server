from abc import ABC, abstractmethod

from sqlalchemy.orm import Session

from src.core.transactional import transactional
from src.payment.domain.card import Card
from src.users.domain.user import User


class GetCardUseCase(ABC):
    @transactional
    @abstractmethod
    def exec(self, user: User, db: Session) -> list[Card]:
        pass
