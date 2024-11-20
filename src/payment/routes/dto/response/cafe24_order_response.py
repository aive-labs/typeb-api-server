from pydantic import BaseModel

from src.payment.domain.cafe24_order import Cafe24Order


class Cafe24OrderResponse(BaseModel):
    order_id: str
    cafe24_order_id: str
    return_url: str
    confirmation_url: str

    @staticmethod
    def from_model(cafe24_order: Cafe24Order):
        return Cafe24OrderResponse(
            order_id=cafe24_order.order_id,
            cafe24_order_id=cafe24_order.cafe24_order_id,
            return_url=cafe24_order.return_url,
            confirmation_url=cafe24_order.confirmation_url,
        )
