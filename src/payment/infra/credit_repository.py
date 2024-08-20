from sqlalchemy import desc, func
from sqlalchemy.orm import Session

from src.core.exceptions.exceptions import ConsistencyException
from src.payment.domain.credit_history import CreditHistory
from src.payment.infra.entity.credit_history_entity import CreditHistoryEntity
from src.payment.infra.entity.remaining_credit_entity import RemainingCreditEntity
from src.payment.service.port.base_credit_repository import BaseCreditRepository
from src.users.domain.user import User


class CreditRepository(BaseCreditRepository):

    def get_remain_credit(self, db: Session) -> int:
        entity = db.query(RemainingCreditEntity).first()

        if not entity:
            raise ConsistencyException(
                "잔여 크레딧 데이터가 존재하지 않습니다. 관리자에게 문의하세요."
            )

        return entity.remaining_credit

    def update_credit(self, update_amount, db: Session):
        db.query(RemainingCreditEntity).update(
            {
                RemainingCreditEntity.remaining_credit: RemainingCreditEntity.remaining_credit
                + update_amount
            }
        )

        db.flush()

    def add_history(self, credit_history: CreditHistory, db: Session) -> CreditHistory:
        entity = credit_history.to_entity()
        db.add(entity)
        db.flush()
        return CreditHistory.model_validate(entity)

    def get_history_with_pagination(self, db, current_page, per_page) -> list[CreditHistory]:
        entities = (
            db.query(CreditHistoryEntity)
            .order_by(desc(CreditHistoryEntity.created_at))
            .offset((current_page - 1) * per_page)
            .limit(per_page)
            .all()
        )
        return [CreditHistory.model_validate(entity) for entity in entities]

    def get_all_history_count(self, db: Session) -> int:
        return db.query(func.count(CreditHistoryEntity.id)).scalar()

    def update_credit_history_status(self, credit_history_id, new_status, user: User, db: Session):
        db.query(CreditHistoryEntity).filter(CreditHistoryEntity.id == credit_history_id).update(
            {
                CreditHistoryEntity.status: new_status,
                CreditHistoryEntity.updated_by: str(user.user_id),
                CreditHistoryEntity.updated_at: func.now(),
            }
        )
