from sqlalchemy.orm import Session

from src.core.exceptions.exceptions import ConsistencyException
from src.payment.domain.credit_history import CreditHistory
from src.payment.infra.entity.remaining_credit_entity import RemainingCreditEntity
from src.payment.service.port.base_credit_repository import BaseCreditRepository


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

    def add_history(self, credit_history: CreditHistory, db: Session):
        pass
