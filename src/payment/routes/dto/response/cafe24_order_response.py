from pydantic import BaseModel


class Cafe24OrderResponse(BaseModel):
    order_id: str
    cafe24_order_id: str
    return_url: str
    confirmation_url: str
