from sqlalchemy.orm import Session

from src.core.transactional import transactional
from src.payment.routes.use_case.delete_card import DeleteCardUseCase
from src.payment.service.port.base_payment_repository import BasePaymentRepository
from src.user.domain.user import User


class DeleteCardService(DeleteCardUseCase):

    def __init__(self, payment_repository: BasePaymentRepository):
        self.payment_repository = payment_repository

    @transactional
    def exec(self, card_id: int, user: User, db: Session):
        card = self.payment_repository.get_card(card_id, db)

        # 카드를 삭제
        self.payment_repository.delete_card(card_id, db)

        if card.is_primary:
            # 만약 삭제된 카드가 대표카드인 경우
            # 대표카드를 제외한 카드 중
            # 가장 먼저 등록된 카드를 대표카드로 설정한다.
            oldest_card = self.payment_repository.get_card_order_by_created_at(db)
            self.payment_repository.update_card_to_primary(oldest_card.card_id, user, db)
