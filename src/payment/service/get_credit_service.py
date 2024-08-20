import math

from sqlalchemy.orm import Session

from src.common.pagination.pagination_base import PaginationBase
from src.common.pagination.pagination_response import PaginationResponse
from src.payment.routes.dto.response.credit_history_response import (
    CreditHistoryResponse,
)
from src.payment.routes.use_case.get_credit import GetCreditUseCase
from src.payment.service.port.base_credit_repository import BaseCreditRepository
from src.payment.service.port.base_payment_repository import BasePaymentRepository


class GetCreditService(GetCreditUseCase):

    def __init__(
        self, payment_repository: BasePaymentRepository, credit_repository: BaseCreditRepository
    ):
        self.payment_repository = payment_repository
        self.credit_repository = credit_repository

    def get_credit(self, db: Session) -> int:
        # 잔여 크레딧 조회
        remaining_credit = self.credit_repository.get_remain_credit(db)
        return remaining_credit

    def get_credit_history(
        self, db: Session, based_on, sort_by, current_page, per_page
    ) -> PaginationResponse[CreditHistoryResponse]:
        credit_histories = self.credit_repository.get_history_with_pagination(
            db, current_page, per_page
        )
        responses = [CreditHistoryResponse(**history.model_dump()) for history in credit_histories]

        all_count = self.credit_repository.get_all_history_count(db)

        pagination = PaginationBase(
            total=all_count,
            per_page=per_page,
            current_page=current_page,
            total_page=math.ceil(all_count / per_page),
        )

        return PaginationResponse[CreditHistoryResponse](items=responses, pagination=pagination)
