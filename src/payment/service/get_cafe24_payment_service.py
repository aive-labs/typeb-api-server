from sqlalchemy.orm import Session

from src.auth.routes.port.base_oauth_service import BaseOauthService
from src.main.exceptions.exceptions import NotFoundException
from src.payment.domain.subscription import Subscription
from src.payment.enum.subscription_status import SubscriptionStatus
from src.payment.routes.dto.response.cafe24_payment_response import (
    Cafe24PaymentResponse,
)
from src.payment.routes.use_case.get_cafe24_payment_usecase import (
    GetCafe24PaymentUseCase,
)
from src.payment.service.port.base_payment_repository import BasePaymentRepository
from src.payment.service.port.base_subscription_repository import (
    BaseSubscriptionRepository,
)
from src.user.domain.user import User


class GetCafe24PaymentService(GetCafe24PaymentUseCase):

    def __init__(
        self,
        cafe24_service: BaseOauthService,
        payment_repository: BasePaymentRepository,
        subscription_repository: BaseSubscriptionRepository,
    ):
        self.cafe24_service = cafe24_service
        self.payment_repository = payment_repository
        self.subscription_repository = subscription_repository

    async def exec(self, order_id: str, user: User, db: Session) -> Cafe24PaymentResponse:
        self.check_existing_order(order_id, db)

        payment_result = await self.cafe24_service.get_payment(order_id, user)

        self.payment_repository.save_cafe24_payment(payment_result, user, db)

        self.pay_for_subscription(user, db)

        return Cafe24PaymentResponse.from_model(payment_result)

    def check_existing_order(self, order_id, db):
        is_existing_order = self.payment_repository.existing_order_by_cafe24_order_id(order_id, db)
        if not is_existing_order:
            raise NotFoundException(detail={"message": "주문 및 결제 정보를 찾지 못했습니다."})

    def pay_for_subscription(self, user, db: Session):
        # subscription 정보 insert
        subscription = self.subscription_repository.get_my_subscription(db)
        new_subscription = self.create_new_subscription(db, user)
        if subscription is None:
            # 첫 구독인 경우
            self.subscription_repository.register_subscription(new_subscription, db)
        else:
            # 기존 구독 존재
            if subscription.is_expired():
                new_subscription.set_id(subscription.get_id())
                self.subscription_repository.update_subscription(new_subscription, db)
            else:
                subscription.extend_end_date()
                self.subscription_repository.update_subscription(subscription, db)

    def create_new_subscription(self, db, user):
        plans = self.subscription_repository.get_plans(db)  # 구독 요금제 1개 뿐임
        new_subscription = Subscription.with_status(plans[0], SubscriptionStatus.ACTIVE.value, user)
        return new_subscription
