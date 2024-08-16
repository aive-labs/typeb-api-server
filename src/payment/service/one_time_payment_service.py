from sqlalchemy.orm import Session

from src.core.exceptions.exceptions import ConsistencyException
from src.payment.domain.credit_history import CreditHistory
from src.payment.routes.dto.request.payment_request import (
    PaymentAuthorizationRequestData,
)
from src.payment.routes.use_case.payment import PaymentUseCase
from src.payment.routes.use_case.payment_gateway import PaymentGateway
from src.payment.service.port.base_credit_repository import BaseCreditRepository
from src.payment.service.port.base_payment_repository import BasePaymentRepository
from src.users.domain.user import User


class OneTimePaymentService(PaymentUseCase):

    def __init__(
        self,
        payment_repository: BasePaymentRepository,
        payment_gateway: PaymentGateway,
        credit_repository: BaseCreditRepository,
    ):
        self.payment_repository = payment_repository
        self.payment_gateway = payment_gateway
        self.credit_repository = credit_repository

    async def exec(
        self,
        user: User,
        db: Session,
        payment_request: PaymentAuthorizationRequestData | None = None,
    ):

        if payment_request is None:
            raise ConsistencyException(detail={"message": "결제 정보 데이터가 존재하지 않습니다."})

        # order_id와 금액이 동일한지 체크
        self.check_is_order_mismatch(payment_request, db)

        # 결제 승인 요청 후 성공하면 결과 객체 반환
        payment = await self.payment_gateway.request_general_payment_approval(payment_request)

        # 성공인 경우 결제 내역 테이블에 저장
        self.payment_repository.save_history(payment, user, db)

        # 잔여 크레딧 업데이트
        self.credit_repository.update_credit(payment.total_amount, db)

        # 크레딧 히스토리에 내역 추가
        credit_history = CreditHistory.after_charge(payment.order_name, payment.total_amount, user)
        self.credit_repository.add_history(credit_history, db)

        # 검증 테이블에 해당 order_id 데이터 삭제
        self.payment_repository.delete_pre_validation_data(payment_request.order_id, db)

        db.commit()

    def check_is_order_mismatch(self, payment_request, db: Session):
        is_mismatch = not self.payment_repository.check_pre_validation_data_for_payment(
            payment_request.order_id, payment_request.amount, db
        )
        if is_mismatch:
            raise ConsistencyException(detail={"message": "주문 정보가 일치하지 않습니다."})
