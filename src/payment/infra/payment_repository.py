from sqlalchemy.orm import Session

from src.payment.infra.entity.pre_data_for_validation import PreDataForValidationEntity
from src.payment.routes.dto.request.pre_data_for_validation import PreDataForValidation
from src.users.domain.user import User


class PaymentRepository:

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
