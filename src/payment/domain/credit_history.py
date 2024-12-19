from datetime import datetime
from typing import Optional

from pydantic import BaseModel

from src.payment.infra.entity.credit_history_entity import CreditHistoryEntity
from src.payment.model.charging_type import ChargingType
from src.payment.model.credit_status import CreditStatus
from src.payment.model.deposit_without_account_status import DepositWithoutAccountStatus
from src.user.domain.user import User


class CreditHistory(BaseModel):
    id: int | None = None
    user_name: str
    description: str
    status: str
    charge_amount: int | None = None
    use_amount: int | None = None
    note: str | None = None
    charging_type: str | None = None
    remaining_amount: int | None = None
    created_by: str
    created_at: Optional[datetime] = None
    updated_by: str
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

    @staticmethod
    def after_charge(order_name: str, charge_amount: int, remaining_amount, user: User):
        return CreditHistory(
            user_name=user.username,
            description=order_name,
            status=CreditStatus.CHARGE_COMPLETE.value,
            charge_amount=charge_amount,
            charging_type=ChargingType.PAYMENT.value,
            remaining_amount=remaining_amount + charge_amount,
            created_by=str(user.user_id),
            updated_by=str(user.user_id),
        )

    @staticmethod
    def from_deposit(deposit_request, account_number, remaining_amount, user: User):
        return CreditHistory(
            user_name=user.username,
            description="크레딧 충전(무통장 입금)",
            status=DepositWithoutAccountStatus.WAITING.value,
            charge_amount=deposit_request.price,
            note=account_number,
            charging_type=ChargingType.DEPOSIT.value,
            remaining_amount=remaining_amount,
            created_by=str(user.user_id),
            updated_by=str(user.user_id),
        )

    def to_entity(self) -> "CreditHistoryEntity":
        return CreditHistoryEntity(
            user_name=self.user_name,
            description=self.description,
            status=self.status,
            charge_amount=self.charge_amount,
            use_amount=self.use_amount,
            note=self.note,
            charging_type=self.charging_type,
            remaining_amount=self.remaining_amount,
            created_by=self.created_by,
            updated_by=self.updated_by,
        )
