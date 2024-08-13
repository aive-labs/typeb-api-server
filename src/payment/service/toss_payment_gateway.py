import base64

import aiohttp
from fastapi import HTTPException

from src.common.utils.get_env_variable import get_env_variable
from src.payment.domain.payment import Payment
from src.payment.infra.dto.response.toss_payment_response import PaymentResponse
from src.payment.routes.use_case.payment_gateway import PaymentGateway


class TossPaymentGateway(PaymentGateway):
    def __init__(self):
        self.secret_key = get_env_variable("toss_secretkey")
        self.payment_authorization_url = get_env_variable("payment_authorization_url")

    async def request_payment_approval(self, payment_data) -> Payment:
        headers = self.get_header()
        payload = self.get_payload(payment_data)

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

    def get_payload(self, payment_request):
        return {
            "paymentKey": payment_request.payment_key,
            "orderId": payment_request.order_id,
            "amount": payment_request.amount,
        }

    def get_header(self):
        test_secret_key = self.secret_key + ":"
        secret_key_credentials = base64.b64encode(test_secret_key.encode()).decode("utf-8")

        return {
            "Authorization": f"Basic {secret_key_credentials}",
            "Content-Type": "application/json",
        }
