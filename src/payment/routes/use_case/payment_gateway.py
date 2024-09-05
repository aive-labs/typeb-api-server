from abc import ABC, abstractmethod

from src.payment.domain.payment import Payment
from src.payment.infra.dto.response.toss_payment_billing_response import (
    TossPaymentBillingResponse,
)
from src.payment.routes.dto.request.payment_request import (
    PaymentRequest,
)


class PaymentGateway(ABC):

    @abstractmethod
    async def request_general_payment_approval(self, payment_data: PaymentRequest) -> Payment:
        pass

    @abstractmethod
    async def request_billing_key(self, payment_data: PaymentRequest) -> TossPaymentBillingResponse:
        pass

    @abstractmethod
    async def request_billing_payment(
        self, payment_data: PaymentRequest, billing_key: str
    ) -> Payment:
        pass

    @abstractmethod
    async def cancel_payment(self, payment_key: str, reason: str) -> Payment:
        pass
