from abc import ABC, abstractmethod

from src.payment.domain.payment import Payment
from src.payment.routes.dto.request.payment_request import (
    PaymentAuthorizationRequestData,
)


class PaymentGateway(ABC):

    @abstractmethod
    async def request_payment_approval(
        self, payment_data: PaymentAuthorizationRequestData
    ) -> Payment:
        pass
