from abc import ABC, abstractmethod

from sqlalchemy.orm import Session

from src.core.transactional import transactional
from src.payment.routes.dto.response.card_response import CardResponse


class GetCardUseCase(ABC):
    @transactional
    @abstractmethod
    def exec(self, db: Session) -> list[CardResponse]:
        pass
