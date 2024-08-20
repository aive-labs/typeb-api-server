from sqlalchemy.orm import Session

from src.payment.domain.pending_deposit import PendingDeposit
from src.payment.infra.entity.pending_deposit_entity import PendingDepositEntity
from src.payment.service.port.base_deposit_repository import BaseDepositRepository


class DepositRepository(BaseDepositRepository):

    def save_pending_depository(self, pending_deposit: PendingDeposit, db: Session):
        entity = PendingDepositEntity(
            price=pending_deposit.price,
            depositor=pending_deposit.depositor,
            expired_at=pending_deposit.expired_at,
            credit_history_id=pending_deposit.credit_history_id,
            has_deposit_made=pending_deposit.has_deposit_made,
            created_by=pending_deposit.created_by,
            updated_by=pending_deposit.updated_by,
        )

        db.add(entity)
        db.flush()
