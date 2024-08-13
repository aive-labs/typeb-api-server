from sqlalchemy.orm import Session

from src.payment.domain.payment import Payment
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
