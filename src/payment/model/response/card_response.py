from datetime import datetime
from typing import Optional

from pydantic import BaseModel

from src.payment.domain.card import Card


class CardResponse(BaseModel):
    card_id: int | None = None
    card_number: str
    card_type: str
    card_company: str
    owner_type: str
    is_primary: bool = False
    created_by: str
    created_at: Optional[datetime] = None

    @staticmethod
    def from_model(card: Card) -> "CardResponse":
        return CardResponse(
            card_id=card.card_id,
            card_number=card.card_number,
            card_type=card.card_type,
            card_company=card.card_company,
            owner_type=card.owner_type,
            is_primary=card.is_primary,
            created_by=card.created_by,
            created_at=card.created_at,
        )
