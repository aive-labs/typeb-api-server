import base64

import aiohttp
from fastapi import HTTPException

from src.common.utils.get_env_variable import get_env_variable
from src.payment.domain.payment import Payment
from src.payment.infra.dto.response.toss_payment_billing_response import (
    TossPaymentBillingResponse,
)
from src.payment.infra.dto.response.toss_payment_response import PaymentResponse
from src.payment.routes.dto.request.payment_request import (
    PaymentAuthorizationRequestData,
)
from src.payment.routes.use_case.payment_gateway import PaymentGateway


class TossPaymentGateway(PaymentGateway):

    def __init__(self):
        self.secret_key = get_env_variable("toss_secretkey")
        self.payment_authorization_url = get_env_variable("payment_authorization_url")
        self.billing_url = get_env_variable("billing_url")

    async def request_payment_approval(self, payment_data) -> Payment:
        headers = self.get_header()
        payload = self.get_payment_approval_payload(payment_data)

        res = await self.request_payment_approval_to_pg(headers, payload)
        payment_response = PaymentResponse(**res)

        return Payment.from_toss_response(payment_response)

    async def request_payment_approval_to_pg(self, headers, payload):
        async with aiohttp.ClientSession() as session:
            async with session.post(
                url=self.payment_authorization_url,
                data=payload,
                headers=headers,
                ssl=False,
            ) as response:
                res = await response.json()

                if response.status != 200:
                    raise HTTPException(
                        status_code=response.status,
                        detail={"code": res["code"], "message": res["message"]},
                    )

        return res

    def get_payment_approval_payload(self, payment_request):
        return {
            "paymentKey": payment_request.payment_key,
            "orderId": payment_request.order_id,
            "amount": payment_request.amount,
        }

    def get_header(self):
        secret_key_credentials = base64.b64encode((self.secret_key + ":").encode()).decode("utf-8")

        return {
            "Authorization": f"Basic {secret_key_credentials}",
            "Content-Type": "application/json",
        }

    async def request_billing_key(
        self, payment_data: PaymentAuthorizationRequestData
    ) -> TossPaymentBillingResponse:
        headers = self.get_header()
        payload = self.get_billing_payload(payment_data)

        res = await self.request_billing_key_to_pg(headers, payload)
        billing_response = TossPaymentBillingResponse(**res)

        return billing_response

    def get_billing_payload(self, payment_request):
        return {
            "customer_key": payment_request.customer_key,
            "auth_key": payment_request.auth_key,
        }

    async def request_billing_key_to_pg(self, headers, payload):
        async with aiohttp.ClientSession() as session:
            async with session.post(
                url=self.billing_url,
                data=payload,
                headers=headers,
                ssl=False,
            ) as response:
                res = await response.json()

                if response.status != 200:
                    raise HTTPException(
                        status_code=response.status,
                        detail={"code": res["code"], "message": res["message"]},
                    )

                return res