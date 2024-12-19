from datetime import datetime

from pydantic import BaseModel

from src.payment.domain.cafe24_payment import Cafe24Payment
from src.payment.model.cafe24_payment_status import Cafe24PaymentStatus


class Cafe24PaymentResponse(BaseModel):
    cafe24_order_id: str
    payment_status: Cafe24PaymentStatus
    title: str
    payment_method: str
    payment_amount: float
    refund_amount: float | None = None
    currency: str
    pay_date: datetime

    @staticmethod
    def from_model(model: Cafe24Payment):
        return Cafe24PaymentResponse(
            cafe24_order_id=model.order_id,
            payment_status=model.payment_status,
            title=model.title,
            payment_method=model.payment_method,
            payment_amount=model.payment_amount,
            refund_amount=model.refund_amount,
            currency=model.currency,
            pay_date=model.pay_date,
        )
