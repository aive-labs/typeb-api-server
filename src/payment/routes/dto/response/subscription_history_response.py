from pydantic import BaseModel

from src.payment.domain.payment import Payment


class SubscriptionHistoryResponse(BaseModel):
    created_at: str
    order_name: str
    status: str
    card_number: str | None = None
    card_type: str | None = None
    card_company: str | None = None

    @staticmethod
    def from_payment(model: Payment):
        return SubscriptionHistoryResponse(
            created_at=model.approved_at,
            order_name=model.order_name,
            status=model.status.value,
            card_number=model.card_number,
            card_type=model.card_type,
            card_company=model.card_company,
        )
