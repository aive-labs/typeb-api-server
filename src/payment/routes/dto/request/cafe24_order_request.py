import uuid

from pydantic import BaseModel, Field

from src.payment.enum.product_type import ProductType


class Cafe24OrderRequest(BaseModel):
    order_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    order_name: str = Field(..., min_length=1)  # 최소 길이 1 설정
    order_amount: int = Field(..., gt=0)  # 0보다 커야함
    product_type: ProductType = Field(default=ProductType.SUBSCRIPTION)
