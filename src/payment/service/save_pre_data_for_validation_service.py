from sqlalchemy.orm import Session

from src.payment.infra.payment_repository import PaymentRepository
from src.payment.model.request.pre_data_for_validation import PreDataForValidation
from src.payment.routes.use_case.save_pre_data_for_validation import (
    SavePreDataForValidation,
)
from src.user.domain.user import User


class SavePreDataForValidationService(SavePreDataForValidation):

    def __init__(self, payment_repository: PaymentRepository):
        self.payment_repository = payment_repository

    def save_pre_data_for_validation(
        self, pre_data_for_validation: PreDataForValidation, user: User, db: Session
    ):
        self.payment_repository.save_pre_data_for_validation(pre_data_for_validation, user, db)
