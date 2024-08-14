from sqlalchemy.orm import Session

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
