from sqlalchemy.orm import Session

from src.core.exceptions.exceptions import ConsistencyException
from src.core.transactional import transactional
from src.payment.infra.payment_repository import PaymentRepository
from src.payment.routes.use_case.change_card_to_primary_usecase import (
    ChangeCardToPrimaryUseCase,
)
from src.users.domain.user import User


class ChangeCardToPrimaryService(ChangeCardToPrimaryUseCase):

    def __init__(self, payment_repository: PaymentRepository):
        self.payment_repository = payment_repository

    @transactional
    def exec(self, card_id: int, user: User, db: Session):
        card = self.payment_repository.get_card(card_id, db)

        if card.is_primary:
            raise ConsistencyException(
                detail={"message": "해당카드는 대표카드로 설정되어 있습니다."}
            )

        self.payment_repository.update_card_to_primary(card_id, user, db)
