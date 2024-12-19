from abc import ABC, abstractmethod

from sqlalchemy.orm import Session

from src.common.pagination.pagination_response import PaginationResponse
from src.payment.model.response.credit_history_response import (
    CreditHistoryResponse,
)


class GetCreditUseCase(ABC):

    @abstractmethod
    def get_credit(self, db: Session) -> int:
        pass

    @abstractmethod
    def get_credit_history(
        self, db: Session, based_on, sort_by, current_page, per_page
    ) -> PaginationResponse[CreditHistoryResponse]:
        pass
