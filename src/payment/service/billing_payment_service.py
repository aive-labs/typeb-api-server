from sqlalchemy.orm import Session

from src.core.exceptions.exceptions import ConsistencyException, NotFoundException
from src.payment.domain.subscription import Subscription
from src.payment.enum.product_type import ProductType
from src.payment.enum.subscription_status import SubscriptionStatus
from src.payment.infra.payment_repository import PaymentRepository
from src.payment.infra.subscription_repository import SubscriptionRepository
from src.payment.routes.dto.request.payment_request import (
    PaymentAuthorizationRequestData,
)
from src.payment.routes.use_case.payment import PaymentUseCase
from src.payment.routes.use_case.payment_gateway import PaymentGateway
from src.payment.service.toss_uuid_key_generator import TossUUIDKeyGenerator
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

        # 대표 카드 조회
        primary_card = self.payment_repository.get_primary_card(db)
        if not primary_card:
            raise NotFoundException(
                detail={
                    "message": "등록된 대표 카드가 없습니다. 플랜 결제를 위해서는 대표 카드가 필요합니다."
                }
            )

        # 구독 중인 요금제 및 가격 조회
        my_subscription = self.subscription_repository.get_my_subscription(db)
        if my_subscription:
            # 현재 구독이 정상 상태인지 확인
            self.check_subscription_is_active(my_subscription)

            # 기존 가입된 경우
            order_name = f"{my_subscription.plan.name} 플랜 결제"
            subscription_price = my_subscription.plan.price
        else:
            # 최초 가입인 경우, 반드시 payment_request 데이터가 존재해야함
            if payment_request:
                plan = self.subscription_repository.find_by_name(payment_request.order_name, db)
                order_name = f"{plan.name} 플랜 결제"
                subscription_price = plan.price

                # 최초 구독을 결제하려는 경우, Pending 상태로 DB에 저장
                new_subscription = Subscription.with_status(
                    plan, SubscriptionStatus.PENDING.value, user
                )
                my_subscription = self.subscription_repository.register_subscription(
                    new_subscription, db
                )
            else:
                raise ConsistencyException(
                    detail={"message": "결제 정보가 존재하지 않습니다. 관리자에게 문의해주세요."}
                )

        # 자동결제로 실행되는 경우 payment_request 값이 필요하기 때문에 조회된 데이터에서 추가
        if payment_request is None:
            payment_request = PaymentAuthorizationRequestData(
                order_id=TossUUIDKeyGenerator.generate("order"),
                order_name=order_name,
                customer_key=primary_card.customer_key,
                amount=subscription_price,
                product_type=ProductType.SUBSCRIPTION,
            )
        else:
            payment_request.order_name = order_name
            payment_request.amount = subscription_price

        # PG사에 자동 결제 요청
        payment = await self.payment_gateway.request_billing_payment(
            payment_request, primary_card.billing_key
        )

        # 성공인 경우 결제 내역 테이블에 저장
        self.payment_repository.save_history(payment, user, db)

        # 결제가 성공하고나서 구독의 상태를 ACTIVE로 변경
        self.subscription_repository.update_status(
            my_subscription, SubscriptionStatus.ACTIVE.value, db
        )

        db.commit()

    def check_subscription_is_active(self, my_subscription):
        if my_subscription.status != SubscriptionStatus.ACTIVE.value:
            raise ConsistencyException(detail={"message": "정상 구독 상태가 아닙니다."})
