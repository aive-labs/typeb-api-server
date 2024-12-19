from datetime import datetime
from typing import Optional

from pydantic import BaseModel

from src.payment.infra.dto.response.toss_payment_billing_response import (
    TossPaymentBillingResponse,
)
from src.payment.infra.entity.card_entity import CardEntity
from src.user.domain.user import User


class Card(BaseModel):
    card_id: int | None = None
    billing_key: str
    customer_key: str
    card_number: str
    card_type: str
    card_company: str
    owner_type: str
    is_primary: bool = False
    created_by: str
    created_at: Optional[datetime] = None
    updated_by: str
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

    def change_primary_card(self):
        self.is_primary = True

    @staticmethod
    def from_toss_payment_response(response: TossPaymentBillingResponse, user: User):
        return Card(
            billing_key=response.billing_key,
            customer_key=response.customer_key,
            card_number=response.card_number,
            card_type=response.card.card_type,
            card_company=response.card_company,
            owner_type=response.card.owner_type,
            created_by=str(user.user_id),
            updated_by=str(user.user_id),
        )

    def to_entity(self) -> "CardEntity":
        return CardEntity(
            billing_key=self.billing_key,
            customer_key=self.customer_key,
            card_number=self.card_number,
            card_type=self.card_type,
            card_company=self.card_company,
            owner_type=self.owner_type,
            is_primary=self.is_primary,
            created_by=self.created_by,
            updated_by=self.updated_by,
        )
