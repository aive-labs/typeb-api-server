from sqlalchemy.orm import Session

from src.main.exceptions.exceptions import NotFoundException
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

    def complete(self, pending_deposit_id, user, db) -> PendingDeposit:
        entity = (
            db.query(PendingDepositEntity)
            .filter(PendingDepositEntity.id == pending_deposit_id)
            .first()
        )
        if entity is None:
            raise NotFoundException(detail={"무통장 입금 정보를 찾지 못했습니다."})

        db.query(PendingDepositEntity).filter(PendingDepositEntity.id == pending_deposit_id).update(
            {
                PendingDepositEntity.has_deposit_made: True,
                PendingDepositEntity.updated_by: str(user.user_id),
            }
        )

        return PendingDeposit.model_validate(entity)

    def get_deposit_by_credit_history_id(self, credit_history_id, db: Session) -> PendingDeposit:
        entity = (
            db.query(PendingDepositEntity)
            .filter(
                PendingDepositEntity.credit_history_id == credit_history_id,
                PendingDepositEntity.has_deposit_made.is_(True),
            )
            .first()
        )

        if entity is None:
            raise NotFoundException(detail={"무통장 입금 정보를 찾지 못했습니다."})

        return PendingDeposit.model_validate(entity)
