from abc import ABC, abstractmethod

from src.payment.domain.payment import Payment
from src.payment.infra.dto.response.toss_payment_billing_response import (
    TossPaymentBillingResponse,
)
from src.payment.routes.dto.request.payment_request import (
    PaymentAuthorizationRequestData,
)


class PaymentGateway(ABC):

    @abstractmethod
    async def request_general_payment_approval(
        self, payment_data: PaymentAuthorizationRequestData
    ) -> Payment:
        pass

    @abstractmethod
    async def request_billing_key(
        self, payment_data: PaymentAuthorizationRequestData
    ) -> TossPaymentBillingResponse:
        pass

    @abstractmethod
    async def request_billing_payment(
        self, payment_data: PaymentAuthorizationRequestData, billing_key: str
    ) -> Payment:
        pass
