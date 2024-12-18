from sqlalchemy import asc, desc, exists, func
from sqlalchemy.orm import Session

from src.core.exceptions.exceptions import NotFoundException
from src.payment.domain.cafe24_order import Cafe24Order
from src.payment.domain.card import Card
from src.payment.domain.payment import Payment
from src.payment.enum.product_type import ProductType
from src.payment.infra.entity.cafe24_order_entity import Cafe24OrderEntity
from src.payment.infra.entity.cafe24_payment_entity import Cafe24PaymentEntity
from src.payment.infra.entity.card_entity import CardEntity
from src.payment.infra.entity.customer_key_entity import MallCustomerKeyMappingEntity
from src.payment.infra.entity.payment_entity import PaymentEntity
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

        print("count")
        print(count)

        return True if count == 1 else False

    def delete_pre_validation_data(self, order_id: str, db: Session):
        db.query(PreDataForValidationEntity).filter(
            PreDataForValidationEntity.order_id == order_id
        ).delete()

    def save_history(
        self, payment: Payment, user: User, db: Session, saved_credit_history_id: int | None = None
    ):
        entity = payment.to_entity(user, saved_credit_history_id)
        db.add(entity)
        db.flush()

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
        db.flush()

    def get_cards(self, db) -> list[Card]:
        entities = db.query(CardEntity).all()
        return [Card.model_validate(entity) for entity in entities]

    def delete_card(self, card_id, db):
        db.query(CardEntity).filter(CardEntity.card_id == card_id).delete()
        db.flush()

    def get_card_order_by_created_at(self, db) -> Card:
        oldest_card = db.query(CardEntity).order_by(asc(CardEntity.created_at)).first()
        return Card.model_validate(oldest_card)

    def get_primary_card(self, db) -> Card:
        primary_card = db.query(CardEntity).filter(CardEntity.is_primary.is_(True)).first()
        return Card.model_validate(primary_card)

    def get_subscription_payment_history(self, db, current_page, per_page) -> list[Payment]:
        entities = (
            db.query(PaymentEntity)
            .filter(PaymentEntity.product_type == ProductType.SUBSCRIPTION.value)
            .order_by(desc(PaymentEntity.created_at))
            .offset((current_page - 1) * per_page)
            .limit(per_page)
            .all()
        )
        return [Payment.model_validate(entity) for entity in entities]

    def get_all_subscription_count(self, db) -> int:
        return (
            db.query(func.count(PaymentEntity.order_id))
            .filter(PaymentEntity.product_type == ProductType.SUBSCRIPTION.value)
            .scalar()
        )

    def get_customer_key(self, mall_id, db) -> str | None:
        entity = (
            db.query(MallCustomerKeyMappingEntity)
            .filter(MallCustomerKeyMappingEntity.mall_id == mall_id)
            .first()
        )

        if entity is None:
            return None

        return entity.customer_key

    def save_customer_key(self, user: User, customer_key, db: Session):
        entity = MallCustomerKeyMappingEntity(
            mall_id=user.mall_id,
            customer_key=customer_key,
            created_by=str(user.user_id),
            updated_by=str(user.user_id),
        )
        db.add(entity)
        db.flush()

    def get_payment_by_credit_history_id(self, credit_history_id, db: Session) -> Payment:
        entity = (
            db.query(PaymentEntity)
            .filter(PaymentEntity.credit_history_id == credit_history_id)
            .first()
        )

        if entity is None:
            raise NotFoundException(detail={"message": "주문 및 결제 정보를 찾지 못했습니다."})

        print(entity)
        return Payment.model_validate(entity)

    def save_cafe24_order(self, cafe24_order: Cafe24Order, user: User, db: Session):
        entity = Cafe24OrderEntity.from_model(cafe24_order, user)
        db.add(entity)

        db.commit()

    def existing_order_by_cafe24_order_id(self, order_id, db):
        return db.query(exists().where(Cafe24OrderEntity.cafe24_order_id == order_id)).scalar()

    def save_cafe24_payment(self, payment_result, user: User, db: Session):
        entity = Cafe24PaymentEntity.from_model(payment_result, user)
        db.add(entity)

        db.commit()
