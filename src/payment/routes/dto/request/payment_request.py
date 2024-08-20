from pydantic import BaseModel

from src.payment.enum.product_type import ProductType


class PaymentAuthorizationRequestData(BaseModel):
    order_id: str
    amount: int
    payment_key: str | None = None
    customer_key: str | None = None
    auth_key: str | None = None
    order_name: str | None = None
    product_type: ProductType
