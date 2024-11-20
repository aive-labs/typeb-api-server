import uuid

from pydantic import BaseModel, Field

from src.payment.enum.product_type import ProductType


class Cafe24OrderRequest(BaseModel):
    order_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    order_name: str
    order_amount: int
    product_type: ProductType = Field(default=ProductType.SUBSCRIPTION)
