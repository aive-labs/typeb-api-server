from abc import ABC, abstractmethod

from sqlalchemy.orm import Session

from src.payment.domain.cafe24_order import Cafe24Order
from src.payment.domain.card import Card
from src.payment.domain.payment import Payment
from src.payment.routes.dto.request.pre_data_for_validation import PreDataForValidation
from src.user.domain.user import User


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
    def save_history(
        self, payment: Payment, user: User, db: Session, saved_credit_history_id: int | None = None
    ):
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

    @abstractmethod
    def get_subscription_payment_history(self, db, current_page, per_page) -> list[Payment]:
        pass

    @abstractmethod
    def get_customer_key(self, mall_id, db) -> str | None:
        pass

    @abstractmethod
    def save_customer_key(self, user: User, customer_key, db: Session):
        pass

    @abstractmethod
    def get_all_subscription_count(self, db) -> int:
        pass

    @abstractmethod
    def get_payment_by_credit_history_id(self, credit_history_id, db: Session) -> Payment:
        pass

    @abstractmethod
    def save_cafe24_order(self, cafe24_order: Cafe24Order, user: User, db: Session):
        pass

    @abstractmethod
    def save_cafe24_payment(self, payment_result, user: User, db: Session):
        pass

    @abstractmethod
    def existing_order_by_cafe24_order_id(self, order_id, db: Session):
        pass
