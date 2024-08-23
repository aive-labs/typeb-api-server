from datetime import datetime, timedelta, timezone

from sqlalchemy.orm import Session

from src.common.slack.slack_message import send_slack_message
from src.core.exceptions.exceptions import BadRequestException
from src.core.transactional import transactional
from src.payment.domain.credit_history import CreditHistory
from src.payment.domain.pending_deposit import PendingDeposit
from src.payment.enum.credit_status import CreditStatus
from src.payment.routes.dto.request.deposit_without_account import DepositWithoutAccount
from src.payment.routes.use_case.deposit_without_account_usecase import (
    DepositWithoutAccountUseCase,
)
from src.payment.service.port.base_credit_repository import BaseCreditRepository
from src.payment.service.port.base_deposit_repository import BaseDepositRepository
from src.users.domain.user import User


class DepositService(DepositWithoutAccountUseCase):
    account_number = "기업은행 1234567890123"

    def __init__(
        self, credit_repository: BaseCreditRepository, deposit_repository: BaseDepositRepository
    ):
        self.credit_repository = credit_repository
        self.deposit_repository = deposit_repository

    @transactional
    def exec(self, deposit_request: DepositWithoutAccount, user: User, db: Session):
        if deposit_request.price <= 0:
            raise BadRequestException(detail={"message": "최소 충전 금액은 0원 이상이어야 합니다."})

        if deposit_request.depositor is None:
            raise BadRequestException(detail={"message": "예금주 명은 필수 입력입니다."})

        # credit_history에 저장
        credit_history = CreditHistory.from_deposit(deposit_request, self.account_number, user)
        credit_history = self.credit_repository.add_history(credit_history, db)

        # 새로운 엔티티에 저장 expired_at, # 입금 상태
        expired_at = datetime.now(timezone.utc) + timedelta(hours=24)
        pending_deposit = PendingDeposit.from_request(
            deposit_request, expired_at, credit_history.id, user
        )
        self.deposit_repository.save_pending_depository(pending_deposit, db)

        send_slack_message(
            title="무통장 입금 확인 요청 🔅",
            body=f"""• 고객사 MALL ID: {user.mall_id} \n • 무통장 입금 신청자: {user.username} \n • 예금주명: {deposit_request.depositor} \n • 금액: {deposit_request.price}  \n """,
        )

    @transactional
    def complete(self, pending_deposit_id, user, db):
        pending_deposit = self.deposit_repository.complete(pending_deposit_id, user, db)
        new_status = CreditStatus.CHARGE_COMPLETE.value
        self.credit_repository.update_credit_history_status(
            pending_deposit.credit_history_id, new_status, user, db
        )
        self.credit_repository.update_credit(pending_deposit.price, db)

        send_slack_message(
            title="무통장 입금 확인 완료 ✅",
            body=f"""• 고객사 MALL ID: {user.mall_id} \n • 무통장 입금 신청자: {user.username} \n • 예금주명: {pending_deposit.depositor} \n • 금액: {pending_deposit.price}  \n """,
        )
