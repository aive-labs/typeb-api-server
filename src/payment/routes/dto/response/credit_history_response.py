from datetime import datetime
from typing import Optional

from pydantic import BaseModel

from src.payment.domain.credit_history import CreditHistory


class CreditHistoryResponse(BaseModel):
    id: int | None = None
    user_name: str
    description: str
    status: str
    amount: int | None = None
    note: str | None = None
    created_at: Optional[datetime] = None

    @staticmethod
    def from_model(model: CreditHistory) -> "CreditHistoryResponse":
        amount = model.charge_amount if model.charge_amount is not None else model.use_amount

        return CreditHistoryResponse(
            id=model.id,
            user_name=model.user_name,
            description=model.description,
            status=model.status,
            amount=amount,
            note=model.note,
            created_at=model.created_at,
        )
