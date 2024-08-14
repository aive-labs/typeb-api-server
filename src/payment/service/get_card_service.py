from sqlalchemy.orm import Session

from src.payment.domain.card import Card
from src.payment.infra.payment_repository import PaymentRepository
from src.payment.routes.use_case.get_card_usecase import GetCardUseCase
from src.users.domain.user import User


class GetCardService(GetCardUseCase):

    def __init__(self, payment_repository: PaymentRepository):
        self.payment_repository = payment_repository

    def exec(self, user: User, db: Session) -> list[Card]:
        return self.payment_repository.get_cards(db)
