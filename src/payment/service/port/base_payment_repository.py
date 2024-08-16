from abc import ABC, abstractmethod

from sqlalchemy.orm import Session

from src.payment.domain.card import Card
from src.payment.domain.payment import Payment
from src.payment.routes.dto.request.pre_data_for_validation import PreDataForValidation
from src.users.domain.user import User


class BasePaymentRepository(ABC):

    @abstractmethod
    def save_pre_data_for_validation(
        self, pre_data_for_validation: PreDataForValidation, user: User, db: Session
    ):
        pass

    @abstractmethod
    def check_pre_validation_data_for_payment(
        self, order_id: str, amount: int, db: Session
    ) -> bool:
        pass

    @abstractmethod
    def delete_pre_validation_data(self, order_id: str, db: Session):
        pass

    @abstractmethod
    def save_history(self, payment: Payment, user: User, db: Session):
        pass

    @abstractmethod
    def save_billing_key(self, card: Card, db: Session):
        pass

    @abstractmethod
    def is_not_exist_primary_card(self, db: Session) -> bool:
        pass

    @abstractmethod
    def get_card(self, card_id, db) -> Card:
        pass

    @abstractmethod
    def get_cards(self, db) -> list[Card]:
        pass

    @abstractmethod
    def delete_card(self, card_id, db):
        pass

    @abstractmethod
    def get_card_order_by_created_at(self, db) -> Card:
        pass

    @abstractmethod
    def update_card_to_primary(self, card_id, user, db):
        pass

    @abstractmethod
    def get_primary_card(self, db) -> Card:
        pass
