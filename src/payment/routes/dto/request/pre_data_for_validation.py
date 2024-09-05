from pydantic import BaseModel


class PreDataForValidation(BaseModel):
    order_id: str
    amount: int
