from sqlalchemy.orm import Session

from src.common.slack.slack_message import send_slack_message
from src.common.utils.get_env_variable import get_env_variable
from src.core.exceptions.exceptions import (
    ConsistencyException,
    PaymentException,
    PolicyException,
)
from src.payment.domain.credit_history import CreditHistory
from src.payment.domain.subscription import Subscription
from src.payment.enum.product_type import ProductType
from src.payment.enum.subscription_status import SubscriptionStatus
from src.payment.routes.dto.request.payment_request import (
    PaymentRequest,
)
from src.payment.routes.use_case.payment import PaymentUseCase
from src.payment.routes.use_case.payment_gateway import PaymentGateway
from src.payment.service.port.base_credit_repository import BaseCreditRepository
from src.payment.service.port.base_payment_repository import BasePaymentRepository
from src.payment.service.port.base_subscription_repository import (
    BaseSubscriptionRepository,
)
from src.users.domain.user import User


class OneTimePaymentService(PaymentUseCase):
    max_retries = 5

    def __init__(
        self,
        payment_repository: BasePaymentRepository,
        payment_gateway: PaymentGateway,
        credit_repository: BaseCreditRepository,
        subscription_repository: BaseSubscriptionRepository,
    ):
        self.payment_repository = payment_repository
        self.payment_gateway = payment_gateway
        self.credit_repository = credit_repository
        self.subscription_repository = subscription_repository

    async def exec(
        self,
        user: User,
        db: Session,
        payment_request: PaymentRequest | None = None,
    ):

        if payment_request is None:
            raise ConsistencyException(detail={"message": "결제 정보 데이터가 존재하지 않습니다."})

        # order_id와 금액이 동일한지 체크(임시 저장한 데이터와 결제 요청 데이터 비교)
        self.check_is_order_mismatch(payment_request.order_id, payment_request.amount, db)

        # 토스페이먼츠에 결제 승인 요청 후 성공하면 결과 객체 반환
        payment = await self.payment_gateway.request_general_payment_approval(payment_request)

        remaining_amount = self.credit_repository.get_remain_credit(db)

        # 실 결제 성공 이후 결제 금액에 대한 크로스 체크(임시 저장한 데이터와 실 결제 데이터 비교)
        self.check_is_order_mismatch(payment.order_id, payment.total_amount, db)

        retry_count = 0
        while retry_count < self.max_retries:
            try:
                # 크레딧 히스토리에 내역 추가
                saved_credit_history_id = None
                if payment_request.product_type == ProductType.CREDIT:
                    print("pay for credit")
                    saved_credit_history_id = self.charge_credit(
                        payment, remaining_amount, user, db
                    )
                elif payment_request.product_type == ProductType.SUBSCRIPTION:
                    print("pay for subscription")
                    self.pay_for_subscription(user, db)
                else:
                    print("raise error")
                    raise PolicyException(detail={"message": "존재하지 않는 결제 상품입니다."})

                # 성공인 경우 결제 내역 테이블에 저장
                self.payment_repository.save_history(payment, user, db, saved_credit_history_id)

                # 검증 테이블에 해당 order_id 데이터 삭제
                self.payment_repository.delete_pre_validation_data(payment_request.order_id, db)

                # 결제 성공 후 종료
                break
            except Exception as e:
                print("retry error")
                print(str(e))

                retry_count += 1
                if retry_count == self.max_retries:
                    cancel_payment = await self.payment_gateway.cancel_payment(
                        payment.payment_key, "결제 데이터 정합성을 위한 취소 요청"
                    )

                    send_slack_message(
                        title="❗️결제 실패 알림(*mall id*: {user.mall_id}*) ❗",
                        body=f"*주문번호*\n"
                        f"• {payment.order_id} \n\n"
                        f"*설명* \n"
                        f"• payment_key: {cancel_payment.payment_key} \n"
                        f"• {cancel_payment.cancel_amount}원 결제 취소 요청 성공 \n\n"
                        f"*에러메시지*  \n"
                        f"• {repr(e)} \n",
                        member_id=get_env_variable("slack_wally"),
                    )

                    raise PaymentException(
                        detail={"message": "결제를 처리하는 도중 문제가 발생했습니다."}
                    )

        db.commit()

    def pay_for_subscription(self, user, db: Session):
        # subscription 정보 insert
        subscription = self.subscription_repository.get_my_subscription(db)
        new_subscription = self.create_new_subscription(db, user)
        if subscription is None:
            # 첫 구독인 경우
            print("first subscription")
            self.subscription_repository.register_subscription(new_subscription, db)
        else:
            # 기존 구독 존재
            print("already subscription")
            if subscription.is_expired():
                print("expired subscription")
                new_subscription.set_id(subscription.get_id())
                self.subscription_repository.update_subscription(new_subscription, db)
            else:
                print("renew subscription")
                subscription.extend_end_date()
                self.subscription_repository.update_subscription(subscription, db)

    def charge_credit(self, payment, remaining_amount, user, db: Session) -> int | None:
        credit_history = CreditHistory.after_charge(
            payment.order_name, payment.total_amount, remaining_amount, user
        )
        saved_history = self.credit_repository.add_history(credit_history, db)
        saved_credit_history_id = saved_history.id
        # 잔여 크레딧 업데이트
        self.credit_repository.update_credit(payment.total_amount, db)
        return saved_credit_history_id

    def create_new_subscription(self, db, user):
        plans = self.subscription_repository.get_plans(db)  # 구독 요금제 1개 뿐임
        new_subscription = Subscription.with_status(plans[0], SubscriptionStatus.ACTIVE.value, user)
        return new_subscription

    def check_is_order_mismatch(self, order_id, amount, db: Session):
        is_match = self.payment_repository.check_pre_validation_data_for_payment(
            order_id, amount, db
        )
        if not is_match:
            raise ConsistencyException(detail={"message": "주문 정보가 일치하지 않습니다."})
