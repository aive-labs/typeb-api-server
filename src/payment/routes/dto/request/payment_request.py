from pydantic import BaseModel


class PaymentAuthorizationRequestData(BaseModel):
    order_id: str
    amount: int
    payment_key: str | None = None
    customer_key: str | None = None
    order_name: str | None = None
