from sqlalchemy.orm import Session

from src.core.exceptions.exceptions import NotFoundException
from src.payment.domain.card import Card
from src.payment.domain.payment import Payment
from src.payment.infra.entity.card_entity import CardEntity
from src.payment.infra.entity.pre_data_for_validation import PreDataForValidationEntity
from src.payment.routes.dto.request.pre_data_for_validation import PreDataForValidation
from src.payment.service.port.base_payment_repository import BasePaymentRepository
from src.users.domain.user import User


class PaymentRepository(BasePaymentRepository):

    def save_pre_data_for_validation(
        self, pre_data_for_validation: PreDataForValidation, user: User, db: Session
    ):
        entity = PreDataForValidationEntity(
            order_id=pre_data_for_validation.order_id,
            amount=pre_data_for_validation.amount,
            created_by=str(user.user_id),
            updated_by=str(user.user_id),
        )

        db.add(entity)

        db.commit()

    def check_pre_validation_data_for_payment(
        self, order_id: str, amount: int, db: Session
    ) -> bool:
        count = (
            db.query(PreDataForValidationEntity)
            .filter(
                PreDataForValidationEntity.order_id == order_id,
                PreDataForValidationEntity.amount == amount,
                ~PreDataForValidationEntity.is_deleted,
            )
            .count()
        )
        return True if count == 1 else False

    def delete_pre_validation_data(self, order_id: str, db: Session):
        db.query(PreDataForValidationEntity).filter(
            PreDataForValidationEntity.order_id == order_id
        ).delete()

    def save_history(self, payment: Payment, user: User, db: Session):
        entity = payment.to_entity(user)
        db.add(entity)

    def save_billing_key(self, card: Card, db: Session):
        entity = card.to_entity()
        db.add(entity)

    def get_card(self, card_id, db) -> Card:
        entity = db.query(CardEntity).filter(CardEntity.card_id == card_id).first()

        if not entity:
            raise NotFoundException(detail={"message": "카드를 찾지 못했습니다."})

        return Card.model_validate(entity)

    def is_not_exist_primary_card(self, db) -> bool:
        entity = db.query(CardEntity).filter(CardEntity.is_primary.is_(True)).first()

        if not entity:
            return True

        return False

    def update_card_to_primary(self, card_id, user, db):
        # 전체 카드를 false로 업데이트하고 해당 카드만 true로 변경
        db.query(CardEntity).update({CardEntity.is_primary: False})
        db.query(CardEntity).filter(CardEntity.card_id == card_id).update(
            {CardEntity.is_primary: True, CardEntity.updated_by: str(user.user_id)}
        )

    def get_cards(self, db) -> list[Card]:
        entities = db.query(CardEntity).all()
        return [Card.model_validate(entity) for entity in entities]
