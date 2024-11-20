from pydantic import BaseModel


class Cafe24Order(BaseModel):
    order_id: str
    cafe24_order_id: str
    order_name: str
    order_amount: int
    currency: str
    return_url: str
    automatic_payment: str
    confirmation_url: str

    @staticmethod
    def from_api_response(data, order_id) -> "Cafe24Order":
        return Cafe24Order(
            order_id=order_id,
            cafe24_order_id=data["order"]["cafe24_order_id"],
            order_name=data["order"]["order_name"],
            order_amount=data["order"]["order_amount"],
            currency=data["order"]["currency"],
            return_url=data["order"]["return_url"],
            automatic_payment=data["order"]["automatic_payment"],
            confirmation_url=data["order"]["confirmation_url"],
        )
