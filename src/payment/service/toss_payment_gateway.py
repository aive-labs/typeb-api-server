import base64

import aiohttp
from fastapi import HTTPException

from src.common.service.aws_service import AwsService
from src.common.utils.get_env_variable import get_env_variable
from src.payment.domain.payment import Payment
from src.payment.enum.product_type import ProductType
from src.payment.infra.dto.response.toss_payment_billing_response import (
    TossPaymentBillingResponse,
)
from src.payment.infra.dto.response.toss_payment_response import TossPaymentResponse
from src.payment.routes.dto.request.payment_request import (
    PaymentRequest,
)
from src.payment.routes.use_case.payment_gateway import PaymentGateway


class TossPaymentGateway(PaymentGateway):

    def __init__(self):
        self.secret_key = AwsService.get_key_from_parameter_store(
            get_env_variable("toss_parameter_store_key")
        )
        self.payment_authorization_url = get_env_variable("payment_authorization_url")
        self.billing_payment_url = get_env_variable("payment_bulling_url")
        self.request_billing_key_url = get_env_variable("billing_url")
        self.payment_cancel_url = get_env_variable("payment_cancel_url")

    async def request_general_payment_approval(self, payment_data) -> Payment:
        headers = self.get_header()
        payload = self.get_payment_approval_payload(payment_data)

        res = await self.request_payment_approval_to_pg(headers, payload)
        payment_response = TossPaymentResponse.from_response(res)

        return Payment.from_toss_response(payment_response, ProductType.CREDIT)

    async def request_payment_approval_to_pg(self, headers, payload):
        async with aiohttp.ClientSession() as session:
            async with session.post(
                url=self.payment_authorization_url,
                json=payload,
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

    async def request_billing_key(self, payment_data: PaymentRequest) -> TossPaymentBillingResponse:
        headers = self.get_header()
        payload = self.get_billing_payload(payment_data)

        res = await self.request_billing_key_to_pg(headers, payload)
        billing_response = TossPaymentBillingResponse.from_response(res)

        return billing_response

    def get_billing_payload(self, payment_request):
        return {
            "customer_key": payment_request.customer_key,
            "auth_key": payment_request.auth_key,
        }

    async def request_billing_key_to_pg(self, headers, payload):
        async with aiohttp.ClientSession() as session:
            async with session.post(
                url=self.request_billing_key_url,
                json=payload,
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

    async def request_billing_payment(
        self, payment_data: PaymentRequest, billing_key: str
    ) -> Payment:
        headers = self.get_header()
        payload = self.get_billing_payment_payload(payment_data)

        res = await self.request_billing_payment_to_pg(headers, payload, billing_key)
        payment_response = TossPaymentResponse.from_response(res)
        return Payment.from_toss_response(payment_response, ProductType.SUBSCRIPTION)

    def get_billing_payment_payload(self, payment_data):
        return {
            "customerKey": payment_data.customer_key,
            "amount": payment_data.amount,
            "orderId": payment_data.order_id,
            "orderName": payment_data.order_name,
        }

    async def request_billing_payment_to_pg(self, headers, payload, billing_key):
        async with aiohttp.ClientSession() as session:
            async with session.post(
                url=f"{self.billing_payment_url}/{billing_key}",
                json=payload,
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

    async def cancel_payment(self, payment_key: str, reason: str) -> Payment:
        headers = self.get_header()
        payload = {"cancelReason": reason}
        response = await self.cancel_payment_to_pg(headers, payload, payment_key)
        payment_response = TossPaymentResponse.from_response(response)
        return Payment.from_toss_response(payment_response, ProductType.SUBSCRIPTION)

    async def cancel_payment_to_pg(self, headers, payload, payment_key: str):
        async with aiohttp.ClientSession() as session:
            async with session.post(
                url=self.payment_cancel_url.replace("{paymentKey}", payment_key),
                json=payload,
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
