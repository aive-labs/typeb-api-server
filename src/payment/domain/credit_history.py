from datetime import datetime
from typing import Optional

from pydantic import BaseModel

from src.payment.enum.credit_status import CreditStatus
from src.users.domain.user import User


class CreditHistory(BaseModel):
    id: int | None = None
    user_name: str
    description: str
    status: str
    charge_amount: int | None = None
    use_amount: int | None = None
    note: str | None = None
    created_by: str
    created_at: Optional[datetime] = None
    updated_by: str
    updated_at: Optional[datetime] = None

    @staticmethod
    def after_charge(order_name: str, charge_amount: int, user: User):
        return CreditHistory(
            user_name=user.username,
            description=order_name,
            status=CreditStatus.CHARGE_COMPLETE.value,
            charge_amount=charge_amount,
            created_by=str(user.user_id),
            updated_by=str(user.user_id),
        )
