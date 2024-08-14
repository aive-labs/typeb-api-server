from abc import ABC, abstractmethod

from sqlalchemy.orm import Session

from src.payment.routes.dto.response.credit_history_response import (
    CreditHistoryResponse,
)


class GetCreditUseCase(ABC):

    @abstractmethod
    def get_credit(self, db: Session) -> int:
        pass

    @abstractmethod
    def get_credit_history(self, db) -> list[CreditHistoryResponse]:
        pass
