from sqlalchemy.orm import Session

from src.payment.infra.payment_repository import PaymentRepository
from src.payment.infra.subscription_repository import SubscriptionRepository
from src.payment.routes.dto.request.payment_request import (
    PaymentAuthorizationRequestData,
)
from src.payment.routes.use_case.payment import PaymentUseCase
from src.payment.routes.use_case.payment_gateway import PaymentGateway
from src.users.domain.user import User


class BillingPaymentService(PaymentUseCase):

    def __init__(
        self,
        payment_repository: PaymentRepository,
        payment_gateway: PaymentGateway,
        subscription_repository: SubscriptionRepository,
    ):
        self.payment_repository = payment_repository
        self.payment_gateway = payment_gateway
        self.subscription_repository = subscription_repository

    async def exec(
        self,
        user: User,
        db: Session,
        payment_request: PaymentAuthorizationRequestData | None = None,
    ):
        # TODO: 자동 결제는 payment_request 값을 만들어서 처리해야 함
        # customer_key 조회 필요
        # order_id 생성 필요
        # order_name 생성 필요
        # 요금제 조회 필요

        if payment_request is None:
            payment_request = PaymentAuthorizationRequestData(
                order_id="order_id",
                order_name="order_name",
                customer_key="customer_key",
                amount=10000,
            )

        # 구독 중인 요금제 및 가격 조회
        my_subscription = self.subscription_repository.get_my_subscription(db)

        # 대표 카드 조회
        primary_card = self.payment_repository.get_primary_card(db)

        payment_request = PaymentAuthorizationRequestData(
            order_id="order_id",
            order_name=f"{my_subscription.plan.name} 플랜 결제",
            customer_key=primary_card.customer_key,
            amount=my_subscription.plan.price,
        )

        # PG사에 자동 결제 요청
        payment = await self.payment_gateway.request_billing_payment(
            payment_request, primary_card.billing_key
        )

        # 성공인 경우 결제 내역 테이블에 저장
        self.payment_repository.save_history(payment, user, db)
