from datetime import datetime
from typing import Optional

from pydantic import BaseModel

from src.payment.routes.dto.request.deposit_without_account import DepositWithoutAccount
from src.user.domain.user import User


class PendingDeposit(BaseModel):
    id: int | None = None
    price: int
    depositor: str
    has_deposit_made: bool = False
    credit_history_id: int
    expired_at: datetime
    created_by: str
    created_at: Optional[datetime] = None
    updated_by: str
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

    @staticmethod
    def from_request(model: DepositWithoutAccount, expired_at, credit_history_id, user: User):
        return PendingDeposit(
            price=model.price,
            depositor=model.depositor,
            expired_at=expired_at,
            has_deposit_made=False,
            credit_history_id=credit_history_id,
            created_by=str(user.user_id),
            updated_by=str(user.user_id),
        )
