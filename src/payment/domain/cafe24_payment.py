from datetime import datetime
from typing import Optional

from pydantic import BaseModel

from src.payment.model.cafe24_payment_status import Cafe24PaymentStatus


class Cafe24Payment(BaseModel):
    order_id: str
    payment_status: Cafe24PaymentStatus
    title: str
    approval_no: str
    payment_gateway_name: str
    payment_method: str
    payment_amount: float
    refund_amount: float | None = None
    currency: str
    locale_code: str
    automatic_payment: str
    pay_date: datetime
    refund_date: Optional[datetime] = None
    expiration_date: Optional[datetime] = None

    @staticmethod
    def from_api_response(data):
        return Cafe24Payment(
            order_id=data["order_id"],
            payment_status=Cafe24PaymentStatus(data["payment_status"]),
            title=data["title"],
            approval_no=data["approval_no"],
            payment_gateway_name=data["payment_gateway_name"],
            payment_method=data["payment_method"],
            payment_amount=float(data["payment_amount"]),
            refund_amount=float(data["refund_amount"]),
            currency=data["currency"],
            locale_code=data["locale_code"],
            automatic_payment=data["automatic_payment"],
            pay_date=data["pay_date"],
            refund_date=data.get("refund_date"),
            expiration_date=data.get("expiration_date"),
        )
