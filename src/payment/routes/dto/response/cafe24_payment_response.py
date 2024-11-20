from datetime import datetime

from pydantic import BaseModel

from src.payment.enum.cafe24_payment_status import Cafe24PaymentStatus


class Cafe24PaymentResponse(BaseModel):
    cafe24_order_id: str
    payment_status: Cafe24PaymentStatus
    title: str
    payment_method: str
    payment_amount: float
    refund_amount: float
    currency: str
    pay_date: datetime
