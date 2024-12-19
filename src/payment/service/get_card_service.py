from sqlalchemy.orm import Session

from src.payment.infra.payment_repository import PaymentRepository
from src.payment.model.response.card_response import CardResponse
from src.payment.routes.use_case.get_card_usecase import GetCardUseCase


class GetCardService(GetCardUseCase):

    def __init__(self, payment_repository: PaymentRepository):
        self.payment_repository = payment_repository

    def exec(self, db: Session) -> list[CardResponse]:
        cards = self.payment_repository.get_cards(db)
        return [CardResponse.from_model(card) for card in cards]
